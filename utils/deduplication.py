from typing import List, Set
import logging
from core.talent import Talent

logger = logging.getLogger(__name__)

class TalentDeduplicator:
    """Handles deduplication of talent records"""
    
    def deduplicate_talents(self, talents: List[Talent]) -> List[Talent]:
        """Remove duplicate talents based on GitHub URL and name"""
        seen_urls: Set[str] = set()
        seen_names: Set[str] = set()
        unique_talents = []
        
        for talent in talents:
            # Primary dedup: GitHub URL
            if talent.github_url and talent.github_url in seen_urls:
                logger.debug(f"Duplicate GitHub URL: {talent.name}")
                continue
                
            # Secondary dedup: Name (case insensitive)
            name_key = talent.name.lower().strip()
            if name_key in seen_names:
                logger.debug(f"Duplicate name: {talent.name}")
                continue
                
            # Add to unique list
            unique_talents.append(talent)
            
            if talent.github_url:
                seen_urls.add(talent.github_url)
            seen_names.add(name_key)
        
        removed_count = len(talents) - len(unique_talents)
        if removed_count > 0:
            logger.info(f" Deduplication: removed {removed_count} duplicates")
            
        return unique_talents
    
    @staticmethod
    def merge_talent_data(existing: Talent, new: Talent) -> Talent:
        """Merge data from new talent into existing talent"""
        # Keep the higher score
        if new.github_score > existing.github_score:
            existing.github_score = new.github_score
        
        # Keep stronger AU connection
        if new.au_strength > existing.au_strength:
            existing.au_strength = new.au_strength
            existing.au_signals = new.au_signals
        
        # Merge sources
        for source in new.sources:
            if source not in existing.sources:
                existing.sources.append(source)
        
        # Merge platform data
        for platform, data in new.platform_data.items():
            if platform not in existing.platform_data:
                existing.platform_data[platform] = data
        
        return existing


# Standalone function for backward compatibility
def deduplicate_talents(talents: List[Talent]) -> List[Talent]:
    """Deduplicate talents using TalentDeduplicator"""
    deduplicator = TalentDeduplicator()
    return deduplicator.deduplicate_talents(talents)
