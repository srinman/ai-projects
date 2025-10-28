#!/usr/bin/env python3
"""
Blog RAG Index Builder for Sridher Manivel's Blog
==================================================

This program crawls blog posts from blog.srinman.com and creates a chunked
RAG (Retrieval-Augmented Generation) index suitable for KAITO RAGEngine.

RAG Pattern Overview:
---------------------
1. Content Extraction: Fetch blog posts and extract meaningful text
2. Chunking: Break content into semantic sections for better retrieval
3. Embedding: Each chunk gets converted to vectors (handled by RAGEngine)
4. Storage: Vectors stored in FAISS database for similarity search
5. Retrieval: User queries find relevant chunks via vector similarity
6. Generation: LLM uses retrieved context to generate accurate responses

Program Structure:
-----------------
1. CONFIGURATION: Define blog URL, chunking parameters
2. CONTENT FETCHING: Crawl blog posts and extract text
3. CONTENT CHUNKING: Split content into meaningful sections
4. METADATA ENRICHMENT: Add author, category, URL, section info
5. INDEX GENERATION: Create RAGEngine-compatible JSON index
6. INDEX VALIDATION: Verify index structure and content quality

Author: Generated for Sridher Manivel's Blog RAG System
Date: October 2025
"""

import json
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from dataclasses import dataclass
import re
import time


# =============================================================================
# SECTION 1: CONFIGURATION
# =============================================================================

@dataclass
class BlogConfig:
    """Configuration for blog crawling and indexing"""
    
    # Blog metadata
    blog_url: str = "https://blog.srinman.com/"
    author: str = "Sridher Manivel"
    category: str = "container"
    
    # Chunking parameters - OPTIMIZED FOR BGE EMBEDDING MODEL
    # Shorter chunks (100-150 words) work better with BGE-small model
    # as they produce higher quality embeddings and better similarity scores
    chunk_size: int = 150  # Target words per chunk (reduced from 300)
    chunk_overlap: int = 30  # Overlapping words between chunks (reduced from 50)
    min_chunk_size: int = 50  # Minimum words to keep a chunk (reduced from 100)
    
    # Output configuration
    output_file_chunked: str = "rag_blog_chunked_index.json"  # 150-word chunks
    output_file_summary: str = "rag_blog_summary_index.json"  # Concise summaries
    index_name_chunked: str = "blog_chunked_index"
    index_name_summary: str = "blog_summary_index"
    
    # Crawling configuration
    request_timeout: int = 10
    delay_between_requests: float = 1.0  # Respectful crawling


# =============================================================================
# SECTION 2: CONTENT FETCHING
# =============================================================================

class BlogCrawler:
    """Fetches blog post content from the website"""
    
    def __init__(self, config: BlogConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'RAG-Index-Builder/1.0 (Educational Purpose)'
        })
    
    def fetch_blog_list(self) -> List[Dict[str, str]]:
        """
        Fetch list of blog posts from the main blog page.
        
        Returns:
            List of dictionaries with title and url for each blog post
        """
        print(f"📡 Fetching blog list from {self.config.blog_url}...")
        
        try:
            response = self.session.get(
                self.config.blog_url,
                timeout=self.config.request_timeout
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            blog_posts = []
            
            # Find all blog post links (adjust selector based on actual HTML structure)
            # Looking for article titles and links
            for article in soup.find_all(['article', 'h2', 'h3']):
                link = article.find('a', href=True)
                if link and link.get('href'):
                    url = link['href']
                    # Make URL absolute if it's relative
                    if not url.startswith('http'):
                        url = self.config.blog_url.rstrip('/') + '/' + url.lstrip('/')
                    
                    # Extract title
                    title = link.get_text(strip=True)
                    
                    if title and url and url != self.config.blog_url:
                        blog_posts.append({
                            'title': title,
                            'url': url
                        })
            
            # Remove duplicates based on URL
            seen_urls = set()
            unique_posts = []
            for post in blog_posts:
                if post['url'] not in seen_urls:
                    seen_urls.add(post['url'])
                    unique_posts.append(post)
            
            print(f"✅ Found {len(unique_posts)} blog posts")
            return unique_posts
            
        except Exception as e:
            print(f"❌ Error fetching blog list: {e}")
            return []
    
    def fetch_blog_content(self, url: str, title: str) -> Optional[Dict[str, str]]:
        """
        Fetch content from a single blog post.
        
        Args:
            url: Blog post URL
            title: Blog post title
            
        Returns:
            Dictionary with title, url, and content
        """
        print(f"📄 Fetching: {title}")
        
        try:
            time.sleep(self.config.delay_between_requests)  # Respectful crawling
            
            response = self.session.get(url, timeout=self.config.request_timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script, style, and navigation elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            # Try to find the main content area (adjust selectors based on actual HTML)
            content = None
            
            # Common content containers in blogs
            for selector in ['article', 'main', '.post-content', '.entry-content', '.content']:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text(separator='\n', strip=True)
                    break
            
            # Fallback: get body text
            if not content:
                content = soup.get_text(separator='\n', strip=True)
            
            # Clean up the content
            content = self._clean_content(content)
            
            print(f"   ✓ Extracted {len(content.split())} words")
            
            return {
                'title': title,
                'url': url,
                'content': content
            }
            
        except Exception as e:
            print(f"   ❌ Error fetching {url}: {e}")
            return None
    
    def _clean_content(self, content: str) -> str:
        """Clean and normalize extracted content"""
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = re.sub(r' +', ' ', content)
        
        # Remove very short lines (likely navigation/footer)
        lines = content.split('\n')
        cleaned_lines = [line for line in lines if len(line.strip()) > 20]
        
        return '\n'.join(cleaned_lines).strip()


# =============================================================================
# SECTION 3: CONTENT CHUNKING
# =============================================================================

class ContentChunker:
    """Intelligently chunks blog content into semantic sections"""
    
    def __init__(self, config: BlogConfig):
        self.config = config
    
    def chunk_content(self, content: str) -> List[Dict[str, str]]:
        """
        Split content into semantic chunks with overlap.
        
        Why Chunking?
        - Large documents → poor embedding quality
        - Chunks → focused, relevant retrievals
        - Overlap → maintains context across boundaries
        
        OPTIMIZATION: Shorter chunks (100-150 words) produce better embeddings
        with BGE-small model, leading to higher similarity scores and better retrieval.
        
        Args:
            content: Full blog post content
            
        Returns:
            List of chunks with text and section information
        """
        # Split into paragraphs first (semantic boundaries)
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = []
        current_word_count = 0
        chunk_number = 1
        
        for para in paragraphs:
            para_word_count = len(para.split())
            
            # If adding this paragraph exceeds chunk size, save current chunk
            if current_word_count + para_word_count > self.config.chunk_size and current_chunk:
                chunks.append({
                    'text': ' '.join(current_chunk),
                    'section_number': chunk_number,
                    'word_count': current_word_count
                })
                
                # Create overlap by keeping last paragraph
                current_chunk = current_chunk[-1:] if current_chunk else []
                current_word_count = len(' '.join(current_chunk).split())
                chunk_number += 1
            
            current_chunk.append(para)
            current_word_count += para_word_count
        
        # Add final chunk if it meets minimum size
        if current_chunk and current_word_count >= self.config.min_chunk_size:
            chunks.append({
                'text': ' '.join(current_chunk),
                'section_number': chunk_number,
                'word_count': current_word_count
            })
        
        return chunks
    
    def create_summary(self, title: str, content: str) -> str:
        """
        Create a concise summary from blog title and content.
        
        Uses extractive summarization: identifies key sentences from the content
        to create a focused summary that works well with BGE embeddings.
        
        Args:
            title: Blog post title
            content: Full blog post content
            
        Returns:
            Concise summary (100-150 words)
        """
        # Extract first paragraph (usually contains main idea)
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and len(p.split()) > 10]
        
        if not paragraphs:
            return title
        
        # Start with title
        summary_parts = [title]
        
        # Add first substantial paragraph
        if paragraphs:
            first_para = paragraphs[0]
            # Limit to ~100 words
            words = first_para.split()[:100]
            summary_parts.append(' '.join(words))
        
        # Look for key technical terms in remaining content
        key_terms = self._extract_key_terms(content)
        if key_terms:
            summary_parts.append(f"Key topics: {', '.join(key_terms[:5])}")
        
        return ' '.join(summary_parts)
    
    def _extract_key_terms(self, content: str) -> List[str]:
        """Extract key technical terms from content"""
        # Common technical terms in cloud/container blogs
        tech_patterns = [
            r'\b(Kubernetes|K8s|AKS|Azure|Istio|Envoy)\b',
            r'\b(container|pod|service|deployment|ingress)\b',
            r'\b(AuthorizationPolicy|JWT|OIDC|EntraID)\b',
            r'\b(scaling|autoscaling|HPA|KEDA)\b',
            r'\b(monitoring|logging|observability)\b',
        ]
        
        found_terms = set()
        for pattern in tech_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            found_terms.update(match.lower() for match in matches)
        
        return sorted(list(found_terms))


# =============================================================================
# SECTION 4: INDEX GENERATION
# =============================================================================

class RAGIndexBuilder:
    """Builds RAGEngine-compatible index from blog content"""
    
    def __init__(self, config: BlogConfig):
        self.config = config
        self.crawler = BlogCrawler(config)
        self.chunker = ContentChunker(config)
    
    def build_chunked_index(self) -> Dict:
        """
        Build index with 150-word chunks for detailed content retrieval.
        
        Use Case: When you need specific technical details and code examples
        from blog posts. Shorter chunks = better embedding quality.
        
        Returns:
            Chunked RAG index dictionary
        """
        print("=" * 70)
        print("🚀 Building CHUNKED RAG Index (150-word chunks)")
        print("=" * 70)
        
        blog_posts = self.crawler.fetch_blog_list()
        
        if not blog_posts:
            print("❌ No blog posts found. Check the blog URL and HTML structure.")
            return {"index_name": self.config.index_name_chunked, "documents": []}
        
        all_documents = []
        
        print(f"\n📚 Processing {len(blog_posts)} blog posts...")
        print("-" * 70)
        
        for i, post in enumerate(blog_posts, 1):
            print(f"\n[{i}/{len(blog_posts)}] {post['title']}")
            
            blog_data = self.crawler.fetch_blog_content(post['url'], post['title'])
            
            if not blog_data:
                continue
            
            # Chunk content into 150-word sections
            chunks = self.chunker.chunk_content(blog_data['content'])
            print(f"   ✓ Created {len(chunks)} chunks (~{self.config.chunk_size} words each)")
            
            for chunk in chunks:
                document = {
                    "text": chunk['text'],
                    "metadata": {
                        "author": self.config.author,
                        "category": self.config.category,
                        "url": blog_data['url'],
                        "title": blog_data['title'],
                        "section": f"Part {chunk['section_number']} of {len(chunks)}",
                        "word_count": chunk['word_count']
                    }
                }
                all_documents.append(document)
        
        index = {
            "index_name": self.config.index_name_chunked,
            "documents": all_documents
        }
        
        print("\n" + "=" * 70)
        print(f"✅ Chunked index built successfully!")
        print(f"   Total chunks: {len(all_documents)}")
        print(f"   Total blog posts: {len(blog_posts)}")
        print(f"   Average chunks per post: {len(all_documents) / len(blog_posts):.1f}")
        print(f"   Chunk size: ~{self.config.chunk_size} words")
        print("=" * 70)
        
        return index
    
    def build_summary_index(self, blog_posts_data: List[Dict]) -> Dict:
        """
        Build index with concise summaries for high-level topic matching.
        
        Use Case: When you need to find which blog posts are relevant
        to a query. Better similarity scores with BGE-small model.
        
        Args:
            blog_posts_data: List of blog post data with content
            
        Returns:
            Summary RAG index dictionary
        """
        print("\n" + "=" * 70)
        print("🚀 Building SUMMARY RAG Index (concise summaries)")
        print("=" * 70)
        
        all_documents = []
        
        for blog_data in blog_posts_data:
            if not blog_data:
                continue
            
            # Create concise summary
            summary = self.chunker.create_summary(blog_data['title'], blog_data['content'])
            
            document = {
                "text": summary,
                "metadata": {
                    "author": self.config.author,
                    "category": self.config.category,
                    "url": blog_data['url'],
                    "title": blog_data['title'],
                    "type": "summary"
                }
            }
            all_documents.append(document)
            print(f"   ✓ {blog_data['title'][:60]}...")
        
        index = {
            "index_name": self.config.index_name_summary,
            "documents": all_documents
        }
        
        print("\n" + "=" * 70)
        print(f"✅ Summary index built successfully!")
        print(f"   Total summaries: {len(all_documents)}")
        print("=" * 70)
        
        return index
    
    def build_index(self) -> tuple[Dict, Dict]:
        """
        Main workflow to build BOTH indexes.
        
        Builds:
        1. Chunked index (150-word chunks) - for detailed retrieval
        2. Summary index (concise summaries) - for topic matching
        
        Returns:
            Tuple of (chunked_index, summary_index)
        """
        print("=" * 70)
        print("🚀 Building RAG Indexes for Sridher Manivel's Blog")
        print("   Generating TWO indexes for optimal retrieval:")
        print("   1. Chunked index (150-word chunks)")
        print("   2. Summary index (concise summaries)")
        print("=" * 70)
        
        # Fetch all blog posts
        blog_posts = self.crawler.fetch_blog_list()
        
        if not blog_posts:
            print("❌ No blog posts found.")
            empty_chunked = {"index_name": self.config.index_name_chunked, "documents": []}
            empty_summary = {"index_name": self.config.index_name_summary, "documents": []}
            return empty_chunked, empty_summary
        
        # Fetch content for all posts
        print(f"\n📚 Fetching content from {len(blog_posts)} blog posts...")
        print("-" * 70)
        
        blog_posts_data = []
        for i, post in enumerate(blog_posts, 1):
            print(f"\n[{i}/{len(blog_posts)}] {post['title']}")
            blog_data = self.crawler.fetch_blog_content(post['url'], post['title'])
            if blog_data:
                blog_posts_data.append(blog_data)
        
        # Build chunked index
        chunked_index = self._build_chunked_from_data(blog_posts_data)
        
        # Build summary index
        summary_index = self.build_summary_index(blog_posts_data)
        
        return chunked_index, summary_index
    
    def _build_chunked_from_data(self, blog_posts_data: List[Dict]) -> Dict:
        """Helper to build chunked index from fetched data"""
        print("\n" + "=" * 70)
        print("🚀 Creating CHUNKED index (150-word chunks)...")
        print("=" * 70)
        
        all_documents = []
        
        for blog_data in blog_posts_data:
            chunks = self.chunker.chunk_content(blog_data['content'])
            print(f"   ✓ {blog_data['title'][:50]}... → {len(chunks)} chunks")
            
            for chunk in chunks:
                document = {
                    "text": chunk['text'],
                    "metadata": {
                        "author": self.config.author,
                        "category": self.config.category,
                        "url": blog_data['url'],
                        "title": blog_data['title'],
                        "section": f"Part {chunk['section_number']} of {len(chunks)}",
                        "word_count": chunk['word_count']
                    }
                }
                all_documents.append(document)
        
        index = {
            "index_name": self.config.index_name_chunked,
            "documents": all_documents
        }
        
        print(f"\n✅ Chunked index: {len(all_documents)} total chunks")
        
        return index
    
    def save_index(self, chunked_index: Dict, summary_index: Dict) -> None:
        """Save both indexes to JSON files"""
        print("\n💾 Saving indexes...")
        
        # Save chunked index
        with open(self.config.output_file_chunked, 'w', encoding='utf-8') as f:
            json.dump(chunked_index, f, indent=2, ensure_ascii=False)
        print(f"   ✓ {self.config.output_file_chunked} ({len(json.dumps(chunked_index)) / 1024:.1f} KB)")
        
        # Save summary index
        with open(self.config.output_file_summary, 'w', encoding='utf-8') as f:
            json.dump(summary_index, f, indent=2, ensure_ascii=False)
        print(f"   ✓ {self.config.output_file_summary} ({len(json.dumps(summary_index)) / 1024:.1f} KB)")
        
        print("✅ Indexes saved successfully!")
    
    def validate_index(self, index: Dict) -> bool:
        """Validate index structure and content quality"""
        print("\n🔍 Validating index...")
        
        if not index.get("documents"):
            print("❌ No documents in index")
            return False
        
        issues = []
        
        for i, doc in enumerate(index["documents"]):
            # Check required fields
            if "text" not in doc:
                issues.append(f"Document {i}: Missing 'text' field")
            elif len(doc["text"].split()) < 50:
                issues.append(f"Document {i}: Text too short ({len(doc['text'].split())} words)")
            
            if "metadata" not in doc:
                issues.append(f"Document {i}: Missing 'metadata' field")
            else:
                required_meta = ["author", "category", "url", "title"]
                for field in required_meta:
                    if field not in doc["metadata"]:
                        issues.append(f"Document {i}: Missing metadata field '{field}'")
        
        if issues:
            print(f"⚠️  Found {len(issues)} issues:")
            for issue in issues[:10]:  # Show first 10 issues
                print(f"   - {issue}")
            if len(issues) > 10:
                print(f"   ... and {len(issues) - 10} more")
            return False
        
        print("✅ Index validation passed!")
        return True


# =============================================================================
# SECTION 5: MAIN EXECUTION
# =============================================================================

def main():
    """
    Main entry point for the RAG index builder.
    
    Usage:
        python build_rag_index.py
    
    Output:
        - rag_blog_chunked_index.json (150-word chunks for detailed retrieval)
        - rag_blog_summary_index.json (concise summaries for topic matching)
    """
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║           Blog RAG Index Builder v2.0                           ║
    ║           For Sridher Manivel's Blog                            ║
    ║                                                                  ║
    ║  Optimized for BGE-small embedding model                        ║
    ║  Generates TWO indexes for better similarity matching:          ║
    ║    • Chunked index (150-word chunks)                            ║
    ║    • Summary index (concise summaries)                          ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize configuration
    config = BlogConfig()
    
    print(f"Configuration:")
    print(f"  Blog URL: {config.blog_url}")
    print(f"  Author: {config.author}")
    print(f"  Chunk size: ~{config.chunk_size} words (optimized for BGE-small)")
    print(f"  Output files:")
    print(f"    • {config.output_file_chunked}")
    print(f"    • {config.output_file_summary}")
    
    # Build the indexes
    builder = RAGIndexBuilder(config)
    
    try:
        # Step 1: Build both indexes
        chunked_index, summary_index = builder.build_index()
        
        # Step 2: Validate indexes
        print("\n" + "=" * 70)
        print("🔍 Validating indexes...")
        print("=" * 70)
        
        chunked_valid = builder.validate_index(chunked_index)
        summary_valid = builder.validate_index(summary_index)
        
        if not chunked_valid or not summary_valid:
            print("\n⚠️  One or more indexes have validation issues but will be saved anyway.")
        
        # Step 3: Save indexes
        builder.save_index(chunked_index, summary_index)
        
        print("\n" + "=" * 70)
        print("🎉 SUCCESS! Your RAG indexes are ready!")
        print("=" * 70)
        print("\n📊 Index Statistics:")
        print(f"   Chunked index: {len(chunked_index['documents'])} chunks")
        print(f"   Summary index: {len(summary_index['documents'])} summaries")
        print("\n💡 Which index to use?")
        print("   • Use SUMMARY index for: 'Which blogs discuss Istio?'")
        print("   • Use CHUNKED index for: 'How do I configure AuthorizationPolicy?'")
        print("\nNext steps:")
        print("1. Ensure RAGEngine is running:")
        print("   kubectl port-forward svc/ragengine-start 8000:80")
        print("\n2. Index the SUMMARY version (recommended to start):")
        print(f"   curl -X POST http://localhost:8000/index \\")
        print(f"     -H 'Content-Type: application/json' \\")
        print(f"     -d @{config.output_file_summary} | jq")
        print("\n3. OR index the CHUNKED version (for detailed queries):")
        print(f"   curl -X POST http://localhost:8000/index \\")
        print(f"     -H 'Content-Type: application/json' \\")
        print(f"     -d @{config.output_file_chunked} | jq")
        print("\n4. Test with example query:")
        print("   curl -X POST http://localhost:8000/v1/chat/completions \\")
        print("     -H 'Content-Type: application/json' \\")
        print("     -d '{")
        print(f'       "index_name": "{config.index_name_summary}",')
        print('       "model": "phi-4-mini-instruct",')
        print('       "messages": [{"role": "user", "content": "list blogs about Istio"}],')
        print('       "max_tokens": 150')
        print("     }' | jq -r '.choices[0].message.content'")
        print("\n" + "=" * 70)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
