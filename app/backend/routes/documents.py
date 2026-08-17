"""Document routes for NEXORA AI."""

from uuid import UUID

from quart import Blueprint, jsonify, request

from db import AsyncSessionLocal
from auth.jwt_utils import get_user_id_from_token
from schemas import DocumentResponse, DocumentListResponse
from services.document_service import DocumentService

documents_bp = Blueprint("documents", __name__, url_prefix="/api/documents")


def get_token_from_header():
    """Extract token from Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise ValueError("Missing or invalid authorization header")
    return auth_header.split(" ")[1]


@documents_bp.route("", methods=["GET"])
async def list_documents():
    """List all documents for the current user."""
    try:
        token = get_token_from_header()
        user_id = get_user_id_from_token(token)

        async with AsyncSessionLocal() as session:
            documents = await DocumentService.list_user_documents(session, user_id)
            return jsonify(
                {
                    "documents": [DocumentResponse.model_validate(doc).model_dump() for doc in documents],
                    "total": len(documents),
                }
            ), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": "Failed to list documents"}), 500


@documents_bp.route("/<doc_id>", methods=["GET"])
async def get_document(doc_id: str):
    """Get a specific document."""
    try:
        token = get_token_from_header()
        user_id = get_user_id_from_token(token)

        async with AsyncSessionLocal() as session:
            document = await DocumentService.get_document_by_id(session, UUID(doc_id))
            if not document or document.user_id != user_id:
                return jsonify({"error": "Document not found"}), 404

            return jsonify(DocumentResponse.model_validate(document).model_dump()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": "Failed to get document"}), 500


@documents_bp.route("/<doc_id>", methods=["DELETE"])
async def delete_document(doc_id: str):
    """Soft delete a document."""
    try:
        token = get_token_from_header()
        user_id = get_user_id_from_token(token)

        async with AsyncSessionLocal() as session:
            document = await DocumentService.get_document_by_id(session, UUID(doc_id))
            if not document or document.user_id != user_id:
                return jsonify({"error": "Document not found"}), 404

            success = await DocumentService.soft_delete_document(session, UUID(doc_id))
            if success:
                return jsonify({"message": "Document deleted"}), 200
            else:
                return jsonify({"error": "Failed to delete document"}), 500
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": "Failed to delete document"}), 500
