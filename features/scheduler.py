"""
Scheduled posting for Postboi.
Allows users to schedule posts for later publication.
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
import uuid


class ScheduledPost:
    """Represents a scheduled post."""

    def __init__(self, post_id: str, image_path: str, caption: str,
                 platforms: List[str], scheduled_time: datetime,
                 status: str = 'pending'):
        """
        Initialize a scheduled post.

        Args:
            post_id: Unique post identifier
            image_path: Path to the image file
            caption: Post caption
            platforms: List of platforms to post to
            scheduled_time: When to publish the post
            status: Post status ('pending', 'published', 'failed', 'cancelled')
        """
        self.post_id = post_id
        self.image_path = image_path
        self.caption = caption
        self.platforms = platforms
        self.scheduled_time = scheduled_time
        self.status = status
        self.created_at = datetime.now()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'post_id': self.post_id,
            'image_path': self.image_path,
            'caption': self.caption,
            'platforms': self.platforms,
            'scheduled_time': self.scheduled_time.isoformat(),
            'status': self.status,
            'created_at': self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ScheduledPost':
        """Create from dictionary."""
        post = cls(
            post_id=data['post_id'],
            image_path=data['image_path'],
            caption=data['caption'],
            platforms=data['platforms'],
            scheduled_time=datetime.fromisoformat(data['scheduled_time']),
            status=data.get('status', 'pending')
        )
        if 'created_at' in data:
            post.created_at = datetime.fromisoformat(data['created_at'])
        return post


class Scheduler:
    """Manages scheduled posts."""

    def __init__(self, schedule_file: str = 'scheduled_posts.json',
                 share_callback=None):
        """
        Initialize Scheduler.

        Args:
            schedule_file: Path to JSON file storing scheduled posts
            share_callback: Callback function to execute posts (should accept image_path, caption, platforms)
        """
        self.schedule_file = schedule_file
        self.share_callback = share_callback
        self.scheduled_posts: Dict[str, ScheduledPost] = {}
        self.scheduler = BackgroundScheduler()

        # Load existing scheduled posts
        self._load_scheduled_posts()

        # Start the scheduler
        self.scheduler.start()

        # Re-schedule pending posts
        self._reschedule_pending_posts()

    def _load_scheduled_posts(self) -> None:
        """Load scheduled posts from file."""
        if os.path.exists(self.schedule_file):
            try:
                with open(self.schedule_file, 'r') as f:
                    data = json.load(f)
                    for post_data in data:
                        post = ScheduledPost.from_dict(post_data)
                        self.scheduled_posts[post.post_id] = post
            except Exception as e:
                print(f"Error loading scheduled posts: {str(e)}")

    def _save_scheduled_posts(self) -> bool:
        """Save scheduled posts to file."""
        try:
            data = [post.to_dict() for post in self.scheduled_posts.values()]
            with open(self.schedule_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving scheduled posts: {str(e)}")
            return False

    def _reschedule_pending_posts(self) -> None:
        """Re-schedule pending posts after app restart."""
        now = datetime.now()
        for post_id, post in list(self.scheduled_posts.items()):
            if post.status == 'pending' and post.scheduled_time > now:
                self._schedule_job(post)
            elif post.status == 'pending' and post.scheduled_time <= now:
                # Mark as failed if scheduled time has passed
                post.status = 'failed'
                self._save_scheduled_posts()

    def _schedule_job(self, post: ScheduledPost) -> None:
        """Schedule a job with APScheduler."""
        trigger = DateTrigger(run_date=post.scheduled_time)
        self.scheduler.add_job(
            func=self._execute_scheduled_post,
            trigger=trigger,
            args=[post.post_id],
            id=post.post_id,
            replace_existing=True
        )

    def _execute_scheduled_post(self, post_id: str) -> None:
        """Execute a scheduled post."""
        post = self.scheduled_posts.get(post_id)
        if not post:
            return

        try:
            # Execute the share callback
            if self.share_callback:
                results = self.share_callback(
                    image_path=post.image_path,
                    caption=post.caption,
                    platforms=post.platforms
                )

                # Check if all platforms succeeded
                all_success = all(success for success, _ in results.values())
                post.status = 'published' if all_success else 'failed'
            else:
                post.status = 'failed'

        except Exception as e:
            print(f"Error executing scheduled post: {str(e)}")
            post.status = 'failed'

        # Save updated status
        self._save_scheduled_posts()

        # TODO: Send notification to user (would require notification service)

    def schedule_post(self, image_path: str, caption: str, platforms: List[str],
                     scheduled_time: datetime) -> Tuple[bool, str]:
        """
        Schedule a post for later.

        Args:
            image_path: Path to the image file
            caption: Post caption
            platforms: List of platforms to post to
            scheduled_time: When to publish the post

        Returns:
            Tuple of (success, message/post_id)
        """
        # Validate scheduled time
        if scheduled_time <= datetime.now():
            return False, "Scheduled time must be in the future"

        # Create scheduled post
        post_id = str(uuid.uuid4())
        post = ScheduledPost(
            post_id=post_id,
            image_path=image_path,
            caption=caption,
            platforms=platforms,
            scheduled_time=scheduled_time
        )

        # Add to scheduled posts
        self.scheduled_posts[post_id] = post

        # Schedule the job
        self._schedule_job(post)

        # Save to file
        if self._save_scheduled_posts():
            return True, post_id
        else:
            return False, "Failed to save scheduled post"

    def get_scheduled_posts(self, status: Optional[str] = None) -> List[ScheduledPost]:
        """
        Get scheduled posts, optionally filtered by status.

        Args:
            status: Filter by status ('pending', 'published', 'failed', 'cancelled')

        Returns:
            List of scheduled posts
        """
        posts = list(self.scheduled_posts.values())
        if status:
            posts = [p for p in posts if p.status == status]
        # Sort by scheduled time
        posts.sort(key=lambda p: p.scheduled_time)
        return posts

    def get_post(self, post_id: str) -> Optional[ScheduledPost]:
        """
        Get a specific scheduled post.

        Args:
            post_id: Post ID

        Returns:
            ScheduledPost or None
        """
        return self.scheduled_posts.get(post_id)

    def cancel_post(self, post_id: str) -> Tuple[bool, str]:
        """
        Cancel a scheduled post.

        Args:
            post_id: Post ID

        Returns:
            Tuple of (success, message)
        """
        post = self.scheduled_posts.get(post_id)
        if not post:
            return False, "Post not found"

        if post.status != 'pending':
            return False, f"Cannot cancel post with status: {post.status}"

        # Remove from scheduler
        try:
            self.scheduler.remove_job(post_id)
        except:
            pass

        # Update status
        post.status = 'cancelled'
        self._save_scheduled_posts()

        return True, "Post cancelled successfully"

    def update_post(self, post_id: str, caption: Optional[str] = None,
                   scheduled_time: Optional[datetime] = None) -> Tuple[bool, str]:
        """
        Update a scheduled post.

        Args:
            post_id: Post ID
            caption: New caption (optional)
            scheduled_time: New scheduled time (optional)

        Returns:
            Tuple of (success, message)
        """
        post = self.scheduled_posts.get(post_id)
        if not post:
            return False, "Post not found"

        if post.status != 'pending':
            return False, f"Cannot update post with status: {post.status}"

        # Update fields
        if caption:
            post.caption = caption

        if scheduled_time:
            if scheduled_time <= datetime.now():
                return False, "Scheduled time must be in the future"
            post.scheduled_time = scheduled_time

            # Reschedule the job
            self._schedule_job(post)

        # Save changes
        if self._save_scheduled_posts():
            return True, "Post updated successfully"
        else:
            return False, "Failed to save changes"

    def shutdown(self) -> None:
        """Shutdown the scheduler."""
        self.scheduler.shutdown()
