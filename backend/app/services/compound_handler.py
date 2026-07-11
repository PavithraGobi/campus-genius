"""Compound question handler for multi-part queries.

This module provides proper handling of compound questions by:
1. Detecting if a question has multiple parts
2. Identifying the main topic
3. Breaking into sub-questions
4. Retrieving context for each sub-question
5. Combining answers into one response
"""

import re
from typing import List, Dict, Tuple, Optional
from app.models.retrieval import RetrievedChunk
from app.services.retrieval_service import retrieve_relevant_chunks


class CompoundQuestionHandler:
    """Handles compound questions with multiple parts."""
    
    # Keywords that indicate a compound question
    COMPOUND_INDICATORS = [
        ' and ', ' & ',
        ', ', '; ',
        '?.*?\\?',  # Multiple question marks
        'list', 'explain', 'describe',
        'what about', 'how about',
        'enumerate', 'tell me', 'give me',
        'layers', 'steps', 'types'
    ]
    
    # Topic mapping for better topic identification
    TOPIC_KEYWORDS = {
        'osi': ['osi', 'osi model', 'osi layers', 'open systems interconnection', 'osi மாடல்'],
        'network_types': ['lan', 'man', 'wan', 'network types', 'network categories'],
        'ip_addressing': ['ip', 'ipv4', 'ipv6', 'subnet', 'ip addressing', 'ip address'],
        'tcp_ip': ['tcp', 'udp', 'tcp/ip', 'transport', 'protocols'],
        'network_layers': ['physical', 'data link', 'network', 'transport', 'session', 'presentation', 'application']
    }
    
    def __init__(self, top_k: int = 10):
        self.top_k = top_k
    
    def is_compound_question(self, query: str) -> bool:
        """Check if a question is compound (has multiple parts)."""
        query_lower = query.lower()
        
        # Check for multiple question marks
        if query.count('?') > 1:
            return True
        
        # Check for compound indicators
        for indicator in self.COMPOUND_INDICATORS:
            if indicator in query_lower:
                return True
        
        # Check for numbered items
        if any(str(i) in query for i in range(1, 10)):
            return True
        
        # Check for list words
        list_words = ['list', 'enumerate', 'mention', 'what are', 'what is']
        for word in list_words:
            if word in query_lower:
                return True
        
        return False
    
    def extract_main_topic(self, query: str) -> str:
        """Extract the main topic from the query."""
        query_lower = query.lower()
        
        # Check each topic
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return topic
        
        # Default: use the first noun phrase
        return "general"
    
    def split_into_sub_questions(self, query: str) -> List[str]:
        """Split compound question into individual sub-questions."""
        query_clean = query.strip()
        query_lower = query_clean.lower()
        
        # Special handling for Tanglish compound questions
        if 'enna' in query_lower and 'sollu' in query_lower:
            parts = []
            # Split by '?' first
            if '?' in query_clean:
                q_parts = query_clean.split('?')
                for i, part in enumerate(q_parts):
                    if part.strip():
                        if i < len(q_parts) - 1:
                            parts.append(part.strip() + '?')
                        else:
                            if part.strip():
                                parts.append(part.strip())
            else:
                parts = [query_clean]
            
            # Further split by 'and'
            final_parts = []
            for part in parts:
                if ' and ' in part:
                    sub_parts = part.split(' and ')
                    final_parts.extend([p.strip() for p in sub_parts if p.strip()])
                else:
                    final_parts.append(part.strip())
            
            return final_parts if final_parts else [query_clean]
        
        # Split by multiple question marks
        if '?' in query_clean:
            parts = [p.strip() + '?' for p in query_clean.split('?') if p.strip()]
            if len(parts) > 1:
                return parts
        
        # Split by 'and' and 'or'
        if ' and ' in query_clean:
            parts = query_clean.split(' and ')
            if len(parts) > 1:
                return [p.strip() for p in parts if p.strip()]
        
        if ' or ' in query_clean:
            parts = query_clean.split(' or ')
            if len(parts) > 1:
                return [p.strip() for p in parts if p.strip()]
        
        # Split by commas
        if ',' in query_clean:
            parts = query_clean.split(',')
            if len(parts) > 1:
                return [p.strip() for p in parts if p.strip()]
        
        # If no split works, treat as single question
        return [query_clean]
    
    def retrieve_for_sub_question(self, sub_query: str, document_id: Optional[str] = None) -> List[RetrievedChunk]:
        """Retrieve chunks for a single sub-question."""
        return retrieve_relevant_chunks(
            query=sub_query,
            top_k=self.top_k,
            document_id=document_id
        )
    
    def _filter_osi_chunks(self, chunks: List[RetrievedChunk]) -> List[RetrievedChunk]:
        """Filter chunks to ONLY keep OSI-related chunks when query is about OSI."""
        osi_keywords = [
            'osi', 'osi model', 'osi மாடல்',
            'physical layer', 'data link layer', 'network layer',
            'transport layer', 'session layer', 'presentation layer', 'application layer',
            '7 layers', 'seven layers', 'ஏழு அடுக்குகள்',
            'osi மாடலின்', 'osi மாடல்'
        ]
        
        filtered = []
        for chunk in chunks:
            chunk_text_lower = chunk.chunk_text.lower()
            # Keep chunk ONLY if it has OSI keywords
            for keyword in osi_keywords:
                if keyword in chunk_text_lower:
                    filtered.append(chunk)
                    break
        
        # If no OSI chunks found, return original chunks (fallback)
        if not filtered:
            return chunks
        
        return filtered
    
    def _extract_osi_layers(self, chunks: List[RetrievedChunk]) -> Dict:
        """Extract OSI layer information from chunks."""
        osi_info = {
            'definition': '',
            'layers': [],
            'explanations': {}
        }
        
        # Keywords for each layer
        layer_keywords = {
            'Physical': ['physical', 'physical layer'],
            'Data Link': ['data link', 'data link layer'],
            'Network': ['network', 'network layer'],
            'Transport': ['transport', 'transport layer'],
            'Session': ['session', 'session layer'],
            'Presentation': ['presentation', 'presentation layer'],
            'Application': ['application', 'application layer']
        }
        
        for chunk in chunks:
            text = chunk.chunk_text.lower()
            
            # Extract definition
            if 'osi model' in text or 'osi மாடல்' in text:
                # Get the sentence with OSI model definition
                sentences = chunk.chunk_text.split('.')
                for sent in sentences:
                    if 'osi model' in sent.lower() or 'osi மாடல்' in sent:
                        if 'framework' in sent.lower() or 'கருத்துருவாக்கமாகும்' in sent:
                            osi_info['definition'] = sent.strip()
                            break
            
            # Extract layers
            for layer_name, keywords in layer_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        if layer_name not in osi_info['layers']:
                            osi_info['layers'].append(layer_name)
                        
                        # Get explanation for this layer
                        sentences = chunk.chunk_text.split('.')
                        for sent in sentences:
                            if keyword in sent.lower() and len(sent) > 20:
                                osi_info['explanations'][layer_name] = sent.strip()
                                break
        
        return osi_info
    
    def handle_compound_query(self, query: str, document_id: Optional[str] = None) -> Dict:
        """Handle a compound question and return structured result."""
        
        # Step 1: Detect if compound
        is_compound = self.is_compound_question(query)
        
        # Step 2: Check if query is about OSI
        query_lower = query.lower()
        is_osi_query = 'osi' in query_lower or 'osi model' in query_lower or 'osi மாடல்' in query_lower
        
        if not is_compound:
            # Simple question - normal retrieval
            chunks = self.retrieve_for_sub_question(query, document_id)
            
            # Filter chunks based on topic
            if is_osi_query:
                chunks = self._filter_osi_chunks(chunks)
            
            return {
                'type': 'simple',
                'sub_questions': [query],
                'chunks': [chunks],
                'is_compound': False
            }
        
        # Step 3: Extract main topic
        main_topic = self.extract_main_topic(query)
        
        # Step 4: Split into sub-questions
        sub_questions = self.split_into_sub_questions(query)
        
        # Step 5: Retrieve for each sub-question
        all_chunks = []
        for sub_q in sub_questions:
            chunks = self.retrieve_for_sub_question(sub_q, document_id)
            
            # Filter chunks based on topic
            if is_osi_query:
                chunks = self._filter_osi_chunks(chunks)
            
            all_chunks.append(chunks)
        
        # Step 6: Deduplicate chunks
        seen_texts = set()
        deduped_chunks = []
        for chunks in all_chunks:
            for chunk in chunks:
                if chunk.chunk_text not in seen_texts:
                    seen_texts.add(chunk.chunk_text)
                    deduped_chunks.append(chunk)
        
        # Step 7: Return result
        return {
            'type': 'compound',
            'main_topic': main_topic,
            'sub_questions': sub_questions,
            'chunks': all_chunks,
            'deduped_chunks': deduped_chunks,
            'is_compound': True
        }


# Global instance
compound_handler = CompoundQuestionHandler(top_k=10)