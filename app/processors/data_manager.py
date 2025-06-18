"""
Data Manager for XML-MCP Template

This module handles data storage and retrieval for the Flask server.
Uses TinyDB for simple JSON-based storage.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from tinydb import TinyDB, Query

logger = logging.getLogger(__name__)


class DataManager:
    """
    Manages data storage and retrieval for processing results
    
    Uses TinyDB for lightweight JSON storage. Can be extended to use
    other databases like SQLite, PostgreSQL, etc.
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize data manager
        
        Args:
            db_path: Path to database file (defaults to storage/data.json)
        """
        if db_path is None:
            base_dir = Path(__file__).parent.parent.parent
            storage_dir = base_dir / "storage"
            storage_dir.mkdir(exist_ok=True)
            db_path = storage_dir / "data.json"
        
        self.db_path = db_path
        self.db = TinyDB(db_path)
        
        logger.info(f"DataManager initialized with database: {db_path}")
    
    def store_result(self, result_id: str, data: Dict[str, Any]) -> bool:
        """
        Store processing result
        
        Args:
            result_id: Unique identifier for the result
            data: Result data to store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add metadata
            data.update({
                'result_id': result_id,
                'stored_at': datetime.now().isoformat(),
                'version': '1.0'
            })
            
            # Check if result already exists
            Result = Query()
            existing = self.db.search(Result.result_id == result_id)
            
            if existing:
                # Update existing
                self.db.update(data, Result.result_id == result_id)
                logger.info(f"Updated existing result: {result_id}")
            else:
                # Insert new
                self.db.insert(data)
                logger.info(f"Stored new result: {result_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error storing result {result_id}: {e}")
            return False
    
    def get_result(self, result_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve processing result by ID
        
        Args:
            result_id: Unique identifier for the result
            
        Returns:
            Result data if found, None otherwise
        """
        try:
            Result = Query()
            results = self.db.search(Result.result_id == result_id)
            
            if results:
                logger.info(f"Retrieved result: {result_id}")
                return results[0]
            else:
                logger.warning(f"Result not found: {result_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving result {result_id}: {e}")
            return None
    
    def list_all(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List all stored results
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of result summaries
        """
        try:
            all_results = self.db.all()
            
            # Sort by stored_at timestamp (most recent first)
            all_results.sort(
                key=lambda x: x.get('stored_at', ''), 
                reverse=True
            )
            
            # Apply limit if specified
            if limit:
                all_results = all_results[:limit]
            
            # Return summary information
            summaries = []
            for result in all_results:
                summary = {
                    'result_id': result.get('result_id'),
                    'processing_id': result.get('processing_id'),
                    'output_id': result.get('output_id'),
                    'input_type': result.get('input_type'),
                    'template': result.get('template'),
                    'status': result.get('status'),
                    'timestamp': result.get('timestamp'),
                    'stored_at': result.get('stored_at'),
                    'word_count': result.get('analysis', {}).get('word_count', 0) if result.get('analysis') else 0,
                    'complexity_score': result.get('analysis', {}).get('complexity_score', 0) if result.get('analysis') else 0
                }
                summaries.append(summary)
            
            logger.info(f"Listed {len(summaries)} results")
            return summaries
            
        except Exception as e:
            logger.error(f"Error listing results: {e}")
            return []
    
    def delete_result(self, result_id: str) -> bool:
        """
        Delete processing result by ID
        
        Args:
            result_id: Unique identifier for the result
            
        Returns:
            True if successful, False otherwise
        """
        try:
            Result = Query()
            deleted = self.db.remove(Result.result_id == result_id)
            
            if deleted:
                logger.info(f"Deleted result: {result_id}")
                return True
            else:
                logger.warning(f"Result not found for deletion: {result_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting result {result_id}: {e}")
            return False
    
    def search_results(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search results based on criteria
        
        Args:
            query: Search criteria (e.g., {'input_type': 'markdown'})
            
        Returns:
            List of matching results
        """
        try:
            Result = Query()
            conditions = []
            
            # Build search conditions
            for key, value in query.items():
                if key == 'input_type':
                    conditions.append(Result.input_type == value)
                elif key == 'template':
                    conditions.append(Result.template == value)
                elif key == 'status':
                    conditions.append(Result.status == value)
                elif key == 'min_complexity':
                    conditions.append(Result.analysis.complexity_score >= value)
                elif key == 'max_complexity':
                    conditions.append(Result.analysis.complexity_score <= value)
            
            # Combine conditions with AND
            if conditions:
                combined_condition = conditions[0]
                for condition in conditions[1:]:
                    combined_condition = combined_condition & condition
                
                results = self.db.search(combined_condition)
            else:
                results = self.db.all()
            
            logger.info(f"Search found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error searching results: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics
        
        Returns:
            Dictionary with statistics
        """
        try:
            all_results = self.db.all()
            
            stats = {
                'total_results': len(all_results),
                'input_types': {},
                'templates': {},
                'status_counts': {},
                'complexity_distribution': {'low': 0, 'medium': 0, 'high': 0},
                'recent_activity': 0
            }
            
            # Count recent activity (last 24 hours)
            from datetime import datetime, timedelta
            recent_cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
            
            for result in all_results:
                # Input types
                input_type = result.get('input_type', 'unknown')
                stats['input_types'][input_type] = stats['input_types'].get(input_type, 0) + 1
                
                # Templates
                template = result.get('template', 'unknown')
                stats['templates'][template] = stats['templates'].get(template, 0) + 1
                
                # Status
                status = result.get('status', 'unknown')
                stats['status_counts'][status] = stats['status_counts'].get(status, 0) + 1
                
                # Complexity distribution
                complexity = result.get('analysis', {}).get('complexity_score', 0)
                if complexity <= 5:
                    stats['complexity_distribution']['low'] += 1
                elif complexity <= 10:
                    stats['complexity_distribution']['medium'] += 1
                else:
                    stats['complexity_distribution']['high'] += 1
                
                # Recent activity
                stored_at = result.get('stored_at', '')
                if stored_at > recent_cutoff:
                    stats['recent_activity'] += 1
            
            logger.info("Generated database statistics")
            return stats
            
        except Exception as e:
            logger.error(f"Error generating statistics: {e}")
            return {}
    
    def cleanup_old_results(self, days_old: int = 30) -> int:
        """
        Clean up old results
        
        Args:
            days_old: Delete results older than this many days
            
        Returns:
            Number of results deleted
        """
        try:
            from datetime import datetime, timedelta
            
            cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()
            
            Result = Query()
            old_results = self.db.search(Result.stored_at < cutoff_date)
            
            if old_results:
                deleted = self.db.remove(Result.stored_at < cutoff_date)
                logger.info(f"Cleaned up {len(deleted)} old results (older than {days_old} days)")
                return len(deleted)
            else:
                logger.info("No old results to clean up")
                return 0
                
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return 0
    
    def backup_database(self, backup_path: Optional[Path] = None) -> bool:
        """
        Create a backup of the database
        
        Args:
            backup_path: Path for backup file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import shutil
            
            if backup_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = self.db_path.parent / f"data_backup_{timestamp}.json"
            
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False