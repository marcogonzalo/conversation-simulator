"""
Command handlers for analysis bounded context.
"""
from typing import List
from uuid import UUID

from src.analysis.application.commands.analyze_conversation import (
    AnalyzeConversationCommand, AnalyzeConversationResult,
    GetAnalysisCommand, GetAnalysisResult,
    UpdateAnalysisCommand, UpdateAnalysisResult,
    DeleteAnalysisCommand, DeleteAnalysisResult
)
from src.analysis.domain.entities.analysis import Analysis, AnalysisStatus
from src.analysis.domain.value_objects.analysis_id import AnalysisId
from src.analysis.domain.value_objects.recommendation import Recommendation
from src.analysis.domain.services.analysis_service import AnalysisService
from src.analysis.domain.repositories.analysis_repository import AnalysisRepository
from src.analysis.domain.exceptions import AnalysisNotFoundError, AnalysisValidationError


class AnalyzeConversationCommandHandler:
    """Handler for analyze conversation command."""
    
    def __init__(
        self,
        analysis_repository: AnalysisRepository,
        analysis_service: AnalysisService
    ):
        self._analysis_repository = analysis_repository
        self._analysis_service = analysis_service
    
    async def handle(self, command: AnalyzeConversationCommand) -> AnalyzeConversationResult:
        """Handle analyze conversation command."""
        try:
            # Validate conversation data
            self._analysis_service.validate_analysis_data(command.conversation_data)
            
            # Check if analysis already exists
            existing_analysis = await self._analysis_repository.get_by_conversation_id(
                command.conversation_id
            )
            if existing_analysis:
                return AnalyzeConversationResult(
                    analysis_id=existing_analysis.id,
                    success=True,
                    message="Analysis already exists for this conversation"
                )
            
            # Create analysis
            analysis_id = AnalysisId.generate()
            analysis = Analysis(
                analysis_id=analysis_id,
                conversation_id=command.conversation_id,
                status=AnalysisStatus.PENDING
            )
            
            # Start analysis
            analysis.start_analysis()
            
            # Extract metrics from conversation
            sales_metrics = self._analysis_service.extract_metrics_from_conversation(
                command.conversation_data
            )
            
            # Calculate overall score
            overall_score = self._analysis_service.calculate_overall_score(sales_metrics)
            
            # Generate recommendations
            recommendations = self._analysis_service.generate_recommendations(sales_metrics)
            
            # Generate feedback
            feedback = self._analysis_service.generate_feedback(sales_metrics, overall_score)
            
            # Complete analysis
            analysis.complete_analysis(
                sales_metrics=sales_metrics,
                overall_score=overall_score,
                feedback=feedback,
                recommendations=recommendations
            )
            
            # Save analysis
            await self._analysis_repository.save(analysis)
            
            return AnalyzeConversationResult(
                analysis_id=analysis_id,
                success=True,
                message="Analysis completed successfully"
            )
        
        except AnalysisValidationError as e:
            return AnalyzeConversationResult(
                analysis_id=None,
                success=False,
                message=str(e)
            )
        except Exception as e:
            return AnalyzeConversationResult(
                analysis_id=None,
                success=False,
                message=f"Failed to analyze conversation: {str(e)}"
            )


class GetAnalysisCommandHandler:
    """Handler for get analysis command."""
    
    def __init__(
        self,
        analysis_repository: AnalysisRepository,
        analysis_service: AnalysisService
    ):
        self._analysis_repository = analysis_repository
        self._analysis_service = analysis_service
    
    async def handle(self, command: GetAnalysisCommand) -> GetAnalysisResult:
        """Handle get analysis command."""
        try:
            analysis_id = AnalysisId(UUID(command.analysis_id))
            analysis = await self._analysis_repository.get_by_id(analysis_id)
            
            if not analysis:
                return GetAnalysisResult(
                    analysis_id=None,
                    success=False,
                    message="Analysis not found"
                )
            
            return GetAnalysisResult(
                analysis_id=analysis_id,
                success=True,
                message="Analysis retrieved successfully"
            )
        
        except (ValueError, TypeError):
            return GetAnalysisResult(
                analysis_id=None,
                success=False,
                message="Invalid analysis ID"
            )
        except Exception as e:
            return GetAnalysisResult(
                analysis_id=None,
                success=False,
                message=f"Failed to get analysis: {str(e)}"
            )


class UpdateAnalysisCommandHandler:
    """Handler for update analysis command."""
    
    def __init__(
        self,
        analysis_repository: AnalysisRepository,
        analysis_service: AnalysisService
    ):
        self._analysis_repository = analysis_repository
        self._analysis_service = analysis_service
    
    async def handle(self, command: UpdateAnalysisCommand) -> UpdateAnalysisResult:
        """Handle update analysis command."""
        try:
            analysis_id = AnalysisId(UUID(command.analysis_id))
            analysis = await self._analysis_repository.get_by_id(analysis_id)
            
            if not analysis:
                return UpdateAnalysisResult(
                    analysis_id=None,
                    success=False,
                    message="Analysis not found"
                )
            
            if analysis.is_completed():
                return UpdateAnalysisResult(
                    analysis_id=None,
                    success=False,
                    message="Cannot update completed analysis"
                )
            
            # Update fields if provided
            if command.feedback is not None:
                analysis._feedback = command.feedback
            
            if command.recommendations is not None:
                # Convert dict recommendations to Recommendation objects
                recommendations = []
                for rec_data in command.recommendations:
                    recommendation = Recommendation(
                        text=rec_data['text'],
                        category=rec_data['category'],
                        priority=rec_data.get('priority', 1)
                    )
                    recommendations.append(recommendation)
                analysis._recommendations = recommendations
            
            if command.metadata is not None:
                for key, value in command.metadata.items():
                    analysis.update_metadata(key, value)
            
            # Save updated analysis
            await self._analysis_repository.save(analysis)
            
            return UpdateAnalysisResult(
                analysis_id=analysis_id,
                success=True,
                message="Analysis updated successfully"
            )
        
        except (ValueError, TypeError):
            return UpdateAnalysisResult(
                analysis_id=None,
                success=False,
                message="Invalid analysis ID"
            )
        except Exception as e:
            return UpdateAnalysisResult(
                analysis_id=None,
                success=False,
                message=f"Failed to update analysis: {str(e)}"
            )


class DeleteAnalysisCommandHandler:
    """Handler for delete analysis command."""
    
    def __init__(
        self,
        analysis_repository: AnalysisRepository,
        analysis_service: AnalysisService
    ):
        self._analysis_repository = analysis_repository
        self._analysis_service = analysis_service
    
    async def handle(self, command: DeleteAnalysisCommand) -> DeleteAnalysisResult:
        """Handle delete analysis command."""
        try:
            analysis_id = AnalysisId(UUID(command.analysis_id))
            
            # Check if analysis exists
            if not await self._analysis_repository.exists(analysis_id):
                return DeleteAnalysisResult(
                    success=False,
                    message="Analysis not found"
                )
            
            # Delete analysis
            success = await self._analysis_repository.delete(analysis_id)
            
            if success:
                return DeleteAnalysisResult(
                    success=True,
                    message="Analysis deleted successfully"
                )
            else:
                return DeleteAnalysisResult(
                    success=False,
                    message="Failed to delete analysis"
                )
        
        except (ValueError, TypeError):
            return DeleteAnalysisResult(
                success=False,
                message="Invalid analysis ID"
            )
        except Exception as e:
            return DeleteAnalysisResult(
                success=False,
                message=f"Failed to delete analysis: {str(e)}"
            )
