"""
Django Views for Smart Sales Analytics

This module contains both API endpoints and frontend views for the application.
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import time
import os
import logging

from .models import UploadedFile, QueryHistory, Conversation, ChatMessage
from .ai.query_engine import get_query_engine
from .ai.chat_service import ChatService
from .etl.processor import ETLProcessor
from .etl.validator import DataValidator
import uuid

logger = logging.getLogger(__name__)


# ============================================
# FRONTEND VIEWS
# ============================================

def home(request):
    """
    Main chat interface for querying sales data.
    """
    context = {
        'page_title': 'Sales Analytics Chat',
        'openai_configured': bool(settings.OPENAI_API_KEY),
    }
    return render(request, 'analytics/chat.html', context)


def upload_page(request):
    """
    File upload page for CSV data.
    """
    context = {
        'page_title': 'Upload Sales Data',
        'max_file_size': settings.MAX_UPLOAD_SIZE,
        'max_file_size_mb': settings.MAX_UPLOAD_SIZE / (1024 * 1024),
    }
    return render(request, 'analytics/upload.html', context)


def agent_chatbot_view(request):
    """
    Unified agent chatbot interface with file upload and chat.
    """
    context = {
        'page_title': 'AI Agent - Smart Sales Analytics',
        'gemini_configured': bool(settings.GEMINI_API_KEY),
    }
    return render(request, 'analytics/agent_chatbot.html', context)


# ============================================
# API ENDPOINTS
# ============================================

@api_view(['POST'])
def query_api(request):
    """
    API endpoint for processing natural language queries.

    POST Body:
        {
            "question": "What are the top 5 products?",
            "language": "en"  # optional, defaults to "en"
        }

    Returns:
        {
            "success": true,
            "question": "...",
            "sql": "...",
            "explanation": "...",
            "results": [...],
            "row_count": 5,
            "columns": [...],
            "summary": "..."
        }
    """
    try:
        # Validate request
        question = request.data.get('question', '').strip()
        language = request.data.get('language', 'en')

        if not question:
            return Response(
                {'success': False, 'error': 'Question is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if OpenAI is configured
        if not settings.OPENAI_API_KEY:
            return Response(
                {'success': False, 'error': 'OpenAI API key is not configured'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Process query
        logger.info(f"Processing query: {question}")
        start_time = time.time()

        query_engine = get_query_engine()
        result = query_engine.process_question(question, language)

        execution_time = time.time() - start_time

        # Save to history
        QueryHistory.objects.create(
            question=question,
            language=language,
            generated_sql=result.get('sql', ''),
            sql_explanation=result.get('explanation', ''),
            result_summary=result.get('summary', ''),
            row_count=result.get('row_count', 0),
            execution_time=execution_time,
            success=result.get('success', False),
            error_message=result.get('error', ''),
            created_by=request.user if request.user.is_authenticated else None
        )

        # Add execution time to result
        result['execution_time'] = round(execution_time, 2)

        return Response(result)

    except Exception as e:
        logger.error(f"Query API error: {str(e)}")
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def upload_api(request):
    """
    API endpoint for uploading and processing CSV files.

    POST: Multipart form data with 'file' field

    Returns:
        {
            "success": true,
            "file_id": 123,
            "filename": "orders.csv",
            "message": "File uploaded and processed successfully",
            "stats": {
                "rows_processed": 100,
                "rows_inserted": 98,
                "rows_failed": 2
            }
        }
    """
    try:
        # Debug logging
        logger.info(f"Upload request received. FILES: {list(request.FILES.keys())}, DATA: {list(request.data.keys())}")

        # Check if file was uploaded
        if 'file' not in request.FILES:
            return Response(
                {'success': False, 'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        uploaded_file = request.FILES['file']

        # Validate file extension
        allowed_extensions = ['.csv', '.xlsx', '.xls']
        file_ext = uploaded_file.name.lower()
        if not any(file_ext.endswith(ext) for ext in allowed_extensions):
            return Response(
                {'success': False, 'error': 'Only CSV and Excel files (.csv, .xlsx, .xls) are allowed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check file size
        if uploaded_file.size > settings.MAX_UPLOAD_SIZE:
            max_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
            return Response(
                {'success': False, 'error': f'File size exceeds {max_mb}MB limit'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save file to database
        file_obj = UploadedFile.objects.create(
            filename=uploaded_file.name,
            file=uploaded_file,
            file_size=uploaded_file.size,
            status='processing',
            uploaded_by=request.user if request.user.is_authenticated else None
        )

        logger.info(f"Processing uploaded file: {uploaded_file.name}")

        try:
            # Save to temporary location
            temp_path = file_obj.file.path

            # Validate file
            is_valid, errors = DataValidator.validate_file(temp_path)

            # Log validation result
            logger.info(f"Validation result: is_valid={is_valid}, errors={errors}")

            if not is_valid:
                file_obj.status = 'failed'
                file_obj.error_message = '\n'.join(errors)
                file_obj.save()

                logger.error(f"Validation failed: {errors}")

                return Response({
                    'success': False,
                    'error': 'File validation failed: ' + '; '.join(errors),
                    'validation_errors': errors
                }, status=status.HTTP_400_BAD_REQUEST)

            # Process with ETL
            processor = ETLProcessor()
            stats = processor.process_csv(temp_path)

            # Update file record
            file_obj.status = 'completed'
            file_obj.row_count = stats.get('rows_processed', 0)
            file_obj.processing_stats = stats
            file_obj.save()

            logger.info(f"File processed successfully: {stats}")

            return Response({
                'success': True,
                'file_id': file_obj.id,
                'filename': file_obj.filename,
                'message': 'File uploaded and processed successfully',
                'stats': stats
            })

        except Exception as e:
            # Update file status to failed
            file_obj.status = 'failed'
            file_obj.error_message = str(e)
            file_obj.save()

            logger.error(f"File processing error: {str(e)}")

            return Response({
                'success': False,
                'error': f'File processing failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"Upload API error: {str(e)}")
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def query_history_api(request):
    """
    API endpoint for retrieving query history.

    Query Parameters:
        - limit: Number of records to return (default: 20)
        - offset: Offset for pagination (default: 0)

    Returns:
        {
            "success": true,
            "total": 100,
            "limit": 20,
            "offset": 0,
            "results": [...]
        }
    """
    try:
        # Get pagination parameters
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))

        # Limit max results
        limit = min(limit, 100)

        # Query history
        total = QueryHistory.objects.count()
        histories = QueryHistory.objects.all()[offset:offset + limit]

        # Serialize results
        results = []
        for history in histories:
            results.append({
                'id': history.id,
                'question': history.question,
                'language': history.language,
                'sql': history.generated_sql,
                'explanation': history.sql_explanation,
                'summary': history.result_summary,
                'row_count': history.row_count,
                'execution_time': history.execution_time,
                'success': history.success,
                'error': history.error_message,
                'created_at': history.created_at.isoformat(),
                'created_by': history.created_by.username if history.created_by else None
            })

        return Response({
            'success': True,
            'total': total,
            'limit': limit,
            'offset': offset,
            'results': results
        })

    except Exception as e:
        logger.error(f"History API error: {str(e)}")
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def upload_history_api(request):
    """
    API endpoint for retrieving upload history.

    Query Parameters:
        - limit: Number of records to return (default: 20)
        - offset: Offset for pagination (default: 0)

    Returns:
        {
            "success": true,
            "total": 50,
            "results": [...]
        }
    """
    try:
        # Get pagination parameters
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))

        # Limit max results
        limit = min(limit, 100)

        # Query uploads
        total = UploadedFile.objects.count()
        uploads = UploadedFile.objects.all()[offset:offset + limit]

        # Serialize results
        results = []
        for upload in uploads:
            results.append({
                'id': upload.id,
                'filename': upload.filename,
                'file_size': upload.file_size,
                'row_count': upload.row_count,
                'status': upload.status,
                'error': upload.error_message,
                'stats': upload.processing_stats,
                'uploaded_at': upload.uploaded_at.isoformat(),
                'uploaded_by': upload.uploaded_by.username if upload.uploaded_by else None
            })

        return Response({
            'success': True,
            'total': total,
            'limit': limit,
            'offset': offset,
            'results': results
        })

    except Exception as e:
        logger.error(f"Upload history API error: {str(e)}")
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def health_check(request):
    """
    Health check endpoint for monitoring.

    Returns:
        {
            "status": "healthy",
            "database": "connected",
            "openai": "configured"
        }
    """
    from .database import ch_manager

    health_status = {
        'status': 'healthy',
        'database': 'unknown',
        'gemini': 'not_configured',
        'openai': 'not_configured'
    }

    # Check ClickHouse connection
    try:
        if ch_manager.test_connection():
            health_status['database'] = 'connected'
        else:
            health_status['database'] = 'disconnected'
            health_status['status'] = 'unhealthy'
    except Exception as e:
        health_status['database'] = f'error: {str(e)}'
        health_status['status'] = 'unhealthy'

    # Check Gemini configuration
    if settings.GEMINI_API_KEY:
        health_status['gemini'] = 'configured'
    else:
        health_status['gemini'] = 'not_configured'

    # Check OpenAI configuration (legacy)
    if settings.OPENAI_API_KEY:
        health_status['openai'] = 'configured'
    else:
        health_status['openai'] = 'not_configured'

    return Response(health_status)


@api_view(['GET'])
def file_data_api(request, file_id):
    """
    API endpoint for retrieving uploaded file data and analytics.

    GET Parameters:
        file_id: ID of the uploaded file

    Returns:
        {
            "success": true,
            "file_info": {...},
            "data": [...],  # CSV data rows (first 100)
            "analytics": {
                "total_revenue": 123456.78,
                "total_orders": 100,
                "avg_order_value": 1234.56,
                "top_products": [...],
                "sales_by_date": [...],
                "sales_by_category": [...],
                "sales_by_location": [...]
            }
        }
    """
    try:
        # Get file
        file_obj = UploadedFile.objects.filter(id=file_id).first()

        if not file_obj:
            return Response(
                {'success': False, 'error': 'File not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Read CSV file
        import pandas as pd

        try:
            file_path = file_obj.file.path
            df = pd.read_csv(file_path, encoding='utf-8-sig')

            # Convert DataFrame to list of dictionaries (limit to first 100 rows for display)
            data_rows = df.head(100).fillna('').to_dict('records')

            # Generate analytics
            analytics = generate_file_analytics(df)

            return Response({
                'success': True,
                'file_info': {
                    'id': file_obj.id,
                    'filename': file_obj.filename,
                    'uploaded_at': file_obj.uploaded_at.isoformat(),
                    'row_count': len(df),
                    'columns': list(df.columns)
                },
                'data': data_rows,
                'analytics': analytics
            })

        except Exception as e:
            logger.error(f"Error reading file data: {str(e)}")
            return Response(
                {'success': False, 'error': f'Error reading file: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    except Exception as e:
        logger.error(f"File data API error: {str(e)}")
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def generate_file_analytics(df):
    """
    Generate analytics data from uploaded CSV file.

    Args:
        df: DataFrame with CSV data

    Returns:
        Dictionary with analytics data
    """
    import pandas as pd

    analytics = {
        'total_revenue': 0,
        'total_orders': 0,
        'avg_order_value': 0,
        'top_products': [],
        'sales_by_date': [],
        'sales_by_category': [],
        'sales_by_location': []
    }

    try:
        # Basic metrics
        if 'total_amount' in df.columns:
            analytics['total_revenue'] = float(df['total_amount'].sum())
            analytics['avg_order_value'] = float(df['total_amount'].mean())

        analytics['total_orders'] = len(df)

        # Top products
        if 'product_name' in df.columns and 'total_amount' in df.columns:
            top_products = df.groupby('product_name')['total_amount'].sum().nlargest(10)
            analytics['top_products'] = [
                {'product': product, 'revenue': float(revenue)}
                for product, revenue in top_products.items()
            ]

        # Sales by date
        if 'order_date' in df.columns and 'total_amount' in df.columns:
            df_temp = df.copy()
            df_temp['order_date'] = pd.to_datetime(df_temp['order_date'])
            sales_by_date = df_temp.groupby(df_temp['order_date'].dt.date)['total_amount'].sum().sort_index()
            analytics['sales_by_date'] = [
                {'date': str(date), 'revenue': float(revenue)}
                for date, revenue in sales_by_date.items()
            ]

        # Sales by category
        if 'category' in df.columns and 'total_amount' in df.columns:
            sales_by_category = df.groupby('category')['total_amount'].sum()
            analytics['sales_by_category'] = [
                {'category': category, 'revenue': float(revenue)}
                for category, revenue in sales_by_category.items()
            ]

        # Sales by location
        if 'province' in df.columns and 'total_amount' in df.columns:
            sales_by_location = df.groupby('province')['total_amount'].sum().nlargest(10)
            analytics['sales_by_location'] = [
                {'location': location, 'revenue': float(revenue)}
                for location, revenue in sales_by_location.items()
            ]

    except Exception as e:
        logger.error(f"Error generating analytics: {str(e)}")

    return analytics


@api_view(['POST'])
def code_chat_api(request):
    """
    Code generation chat API endpoint.

    POST Body:
        {
            "message": "Show me the top 5 products by revenue in a bar chart",
            "file_id": 123,  # ID of uploaded CSV file to analyze
            "session_id": "optional-session-id"
        }

    Returns:
        {
            "success": true,
            "message": "Generated visualization showing...",
            "code": "# Python code...",
            "output": "Text output from code execution",
            "plot_url": "/media/plots/plot_123.png",
            "session_id": "abc-123"
        }
    """
    try:
        # Validate request
        message = request.data.get('message', '').strip()
        file_id = request.data.get('file_id')
        session_id = request.data.get('session_id')

        if not message:
            return Response(
                {'success': False, 'error': 'Message is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not file_id:
            return Response(
                {'success': False, 'error': 'file_id is required for code analysis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if Gemini is configured
        if not settings.GEMINI_API_KEY:
            return Response(
                {'success': False, 'error': 'Gemini API key is not configured'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Get the uploaded file
        file_obj = UploadedFile.objects.filter(id=file_id).first()
        if not file_obj:
            return Response(
                {'success': False, 'error': 'File not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Load CSV data
        import pandas as pd
        try:
            df = pd.read_csv(file_obj.file.path, encoding='utf-8-sig')
        except Exception as e:
            logger.error(f"Error loading CSV: {str(e)}")
            return Response(
                {'success': False, 'error': f'Error loading CSV file: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Get or create conversation
        if session_id:
            conversation = Conversation.objects.filter(session_id=session_id).first()
            if not conversation:
                conversation = Conversation.objects.create(
                    session_id=session_id,
                    created_by=request.user if request.user.is_authenticated else None
                )
        else:
            session_id = str(uuid.uuid4())
            conversation = Conversation.objects.create(
                session_id=session_id,
                created_by=request.user if request.user.is_authenticated else None
            )

        # Get conversation history
        messages = conversation.messages.all()
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # Save user message
        ChatMessage.objects.create(
            conversation=conversation,
            role='user',
            content=message
        )

        # Use CodeAnalystService to generate and execute code
        from .ai.code_analyst import CodeAnalystService
        code_analyst = CodeAnalystService()

        result = code_analyst.analyze_data(message, df, conversation_history)

        if not result['success']:
            # Save error message
            ChatMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content=f"I encountered an error: {result.get('error', 'Unknown error')}",
                metadata={'error': result.get('error')}
            )

            return Response({
                'success': False,
                'error': result.get('error'),
                'message': f"I encountered an error while analyzing your data: {result.get('error')}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Build response message
        response_message = "I've analyzed your data"
        if result.get('plot_url'):
            response_message += " and created a visualization for you"
        if result.get('output'):
            response_message += f":\n\n{result['output']}"

        # Save assistant message with metadata
        ChatMessage.objects.create(
            conversation=conversation,
            role='assistant',
            content=response_message,
            metadata={
                'code': result['code'],
                'plot_url': result.get('plot_url'),
                'execution_time': result.get('execution_time')
            }
        )

        return Response({
            'success': True,
            'message': response_message,
            'code': result['code'],
            'output': result.get('output', ''),
            'plot_url': result.get('plot_url'),
            'execution_time': result.get('execution_time', 0),
            'session_id': session_id
        })

    except Exception as e:
        logger.error(f"Code chat API error: {str(e)}")
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def agent_chat_api(request):
    """
    Autonomous agent chat API with ReAct loop.

    POST Body:
        {
            "message": "Show me the top 5 products",
            "file_id": 123,  # Required: ID of uploaded CSV file
            "session_id": "optional-session-id",
            "show_reasoning": false  # Optional: show agent reasoning steps
        }

    Returns:
        {
            "success": true,
            "message": "Here are the top 5 products...",
            "reasoning_steps": [...],  # If show_reasoning=true
            "plot_url": "/media/plots/plot_123.png",  # If plot generated
            "iterations": 3,
            "session_id": "abc-123"
        }
    """
    try:
        # Validate request
        message = request.data.get('message', '').strip()
        file_id = request.data.get('file_id')
        session_id = request.data.get('session_id')
        show_reasoning = request.data.get('show_reasoning', False)

        if not message:
            return Response(
                {'success': False, 'error': 'Message is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not file_id:
            return Response(
                {'success': False, 'error': 'file_id is required. Please upload a CSV file first.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check Gemini configuration
        if not settings.GEMINI_API_KEY:
            return Response(
                {'success': False, 'error': 'Gemini API key is not configured'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Get uploaded file
        file_obj = UploadedFile.objects.filter(id=file_id).first()
        if not file_obj:
            return Response(
                {'success': False, 'error': 'File not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Load CSV into DataFrame
        import pandas as pd
        try:
            df = pd.read_csv(file_obj.file.path, encoding='utf-8-sig')
            logger.info(f"Loaded DataFrame: {len(df)} rows, {len(df.columns)} columns")
        except Exception as e:
            logger.error(f"Error loading CSV: {str(e)}")
            return Response(
                {'success': False, 'error': f'Error loading CSV file: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Get or create conversation
        if session_id:
            conversation = Conversation.objects.filter(session_id=session_id).first()
            if not conversation:
                conversation = Conversation.objects.create(
                    session_id=session_id,
                    created_by=request.user if request.user.is_authenticated else None
                )
        else:
            session_id = str(uuid.uuid4())
            conversation = Conversation.objects.create(
                session_id=session_id,
                created_by=request.user if request.user.is_authenticated else None
            )

        # Get conversation history
        messages = conversation.messages.all()[:10]  # Last 10 messages
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(messages)
        ]

        # Save user message
        ChatMessage.objects.create(
            conversation=conversation,
            role='user',
            content=message
        )

        # Initialize agent and run ReAct loop
        from .ai.agent_service import AgentService
        agent = AgentService()

        logger.info(f"Starting agent ReAct loop for: {message[:50]}...")
        result = agent.run_react_loop(
            user_message=message,
            df=df,
            conversation_history=conversation_history,
            show_reasoning=show_reasoning
        )

        if not result['success']:
            # Save error message
            ChatMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content=f"I encountered an error: {result.get('error', 'Unknown error')}",
                metadata={'error': result.get('error')}
            )

            return Response({
                'success': False,
                'error': result.get('error'),
                'message': result.get('message', 'An error occurred during analysis.')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Save assistant message
        ChatMessage.objects.create(
            conversation=conversation,
            role='assistant',
            content=result['message'],
            metadata={
                'reasoning_steps': result.get('reasoning_steps', []),
                'plot_url': result.get('plot_url'),
                'iterations': result.get('iterations', 0)
            }
        )

        return Response({
            'success': True,
            'message': result['message'],
            'reasoning_steps': result.get('reasoning_steps', []),
            'plot_url': result.get('plot_url'),
            'iterations': result.get('iterations', 0),
            'session_id': session_id
        })

    except Exception as e:
        logger.error(f"Agent chat API error: {str(e)}", exc_info=True)
        return Response(
            {'success': False, 'error': str(e), 'message': f'An unexpected error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def chat_api(request):
    """
    ChatGPT-powered conversational API endpoint.

    POST Body:
        {
            "message": "What are the top selling products?",
            "session_id": "optional-session-id",  # If not provided, creates new conversation
            "auto_query": true  # Whether to automatically query database for data questions
        }

    Returns:
        {
            "success": true,
            "message": "Here are the top selling products...",
            "session_id": "abc-123",
            "query_results": {...},  # Optional, if database was queried
            "conversation_history": [...]  # Recent messages
        }
    """
    try:
        # Validate request
        message = request.data.get('message', '').strip()
        session_id = request.data.get('session_id')
        auto_query = request.data.get('auto_query', True)

        if not message:
            return Response(
                {'success': False, 'error': 'Message is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if OpenAI is configured
        if not settings.OPENAI_API_KEY:
            return Response(
                {'success': False, 'error': 'OpenAI API key is not configured'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Get or create conversation
        if session_id:
            conversation = Conversation.objects.filter(session_id=session_id).first()
            if not conversation:
                conversation = Conversation.objects.create(
                    session_id=session_id,
                    created_by=request.user if request.user.is_authenticated else None
                )
        else:
            # Create new conversation
            session_id = str(uuid.uuid4())
            conversation = Conversation.objects.create(
                session_id=session_id,
                created_by=request.user if request.user.is_authenticated else None
            )

        # Get conversation history
        messages = conversation.messages.all()
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # Save user message
        ChatMessage.objects.create(
            conversation=conversation,
            role='user',
            content=message
        )

        # Get ChatGPT response
        chat_service = ChatService()
        result = chat_service.chat(
            message=message,
            conversation_history=conversation_history,
            auto_query=auto_query
        )

        if not result.get('success'):
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Save assistant message
        assistant_message = ChatMessage.objects.create(
            conversation=conversation,
            role='assistant',
            content=result['message'],
            metadata={
                'query_results': result.get('query_results'),
                'needs_data': result.get('needs_data', False)
            }
        )

        # Get updated conversation history (last 10 messages)
        recent_messages = conversation.messages.all()[:10]
        conversation_history = [
            {
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            }
            for msg in reversed(recent_messages)
        ]

        return Response({
            'success': True,
            'message': result['message'],
            'session_id': session_id,
            'query_results': result.get('query_results'),
            'conversation_history': conversation_history
        })

    except Exception as e:
        logger.error(f"Chat API error: {str(e)}")
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
