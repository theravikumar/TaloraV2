# job_pipeline/storage/embedding_store.py
"""
FAISS-based embedding storage for jobs.
Maps job expectations to embeddings for fast similarity search.
"""

from typing import List, Dict, Tuple
from shared.embeddings import embedding_generator, FAISSIndex
from shared.schema import JobDescriptionProfile


class JobEmbeddingStore:
    """
    Manages embeddings for job expectations.
    Each work unit gets embedded separately for fine-grained matching.
    """
    
    def __init__(self):
        self.generator = embedding_generator
        self.index = FAISSIndex()
        self.workunit_metadata = []  # List of (job_id, expectation_type, wu_index)
    
    def add_job(self, job_id: str, jd_profile: JobDescriptionProfile):
        """
        Add all work units from a job to the index.
        
        Args:
            job_id: Unique job identifier
            jd_profile: Normalized job description profile
        """
        texts_to_embed = []
        metadata = []
        
        # Add required expectations
        for exp_idx, expectation in enumerate(jd_profile['required_expectations']):
            for wu_idx, work_unit in enumerate(expectation['work_units']):
                # Create text representation of work unit
                text = self._workunit_to_text(work_unit)
                texts_to_embed.append(text)
                metadata.append({
                    'job_id': job_id,
                    'expectation_type': 'required',
                    'expectation_idx': exp_idx,
                    'work_unit_idx': wu_idx,
                })
        
        # Add preferred expectations
        for exp_idx, expectation in enumerate(jd_profile['preferred_expectations']):
            for wu_idx, work_unit in enumerate(expectation['work_units']):
                text = self._workunit_to_text(work_unit)
                texts_to_embed.append(text)
                metadata.append({
                    'job_id': job_id,
                    'expectation_type': 'preferred',
                    'expectation_idx': exp_idx,
                    'work_unit_idx': wu_idx,
                })
        
        if not texts_to_embed:
            print(f"Warning: No work units to embed for job {job_id}")
            return
        
        # Generate embeddings
        embeddings = self.generator.embed_batch(texts_to_embed)
        
        # Create IDs for FAISS
        ids = [f"{job_id}:{meta['expectation_type']}:{meta['expectation_idx']}:{meta['work_unit_idx']}" 
               for meta in metadata]
        
        # Add to index
        self.index.add(embeddings, ids)
        self.workunit_metadata.extend(metadata)
        
        print(f"[OK] Added {len(texts_to_embed)} work units for job {job_id}")
    
    def _workunit_to_text(self, work_unit: Dict) -> str:
        """
        Convert work unit to embeddable text.
        
        Format: "action object using tools with constraints"
        Example: "Build scalable backend APIs using Python, FastAPI with 5+ years experience, 1M+ requests/day"
        """
        parts = [
            work_unit['action'],
            work_unit['object']
        ]
        
        if work_unit['tools']:
            parts.append("using " + ", ".join(work_unit['tools']))
        
        if work_unit['constraints']:
            parts.append("with " + ", ".join(work_unit['constraints']))
        
        return " ".join(parts)
    
    def search_similar_jobs(self, resume_workunit_text: str, k: int = 10) -> List[Tuple[str, float]]:
        """
        Find jobs with similar work units to resume.
        
        Args:
            resume_workunit_text: Text representation of resume work unit
            k: Number of results
            
        Returns:
            List of (job_id, distance) tuples
        """
        # Embed query
        query_embedding = self.generator.embed(resume_workunit_text)
        
        # Search
        results = self.index.search(query_embedding, k=k)
        
        # Extract job_ids (removing work unit specifics)
        job_distances = {}
        for id_str, distance in results:
            job_id = id_str.split(':')[0]
            # Keep minimum distance for each job
            if job_id not in job_distances or distance < job_distances[job_id]:
                job_distances[job_id] = distance
        
        # Sort by distance
        sorted_jobs = sorted(job_distances.items(), key=lambda x: x[1])
        
        return sorted_jobs
    
    def save(self):
        """Save index to disk"""
        self.index.save()
        print(f"[OK] Saved {len(self.index)} embeddings to disk")
    
    def load(self):
        """Load index from disk"""
        self.index.load()
        print(f"[OK] Loaded {len(self.index)} embeddings from disk")
    
    def __len__(self):
        """Get number of work units indexed"""
        return len(self.index)


# Singleton
job_embedding_store = JobEmbeddingStore()
