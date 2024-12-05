document.addEventListener('DOMContentLoaded', function() {
    const videoContainers = document.querySelectorAll('.video-container');
    
    videoContainers.forEach(container => {
        const thumbnail = container.querySelector('.video-thumbnail');
        const video = container.querySelector('video');
        
        if (!thumbnail || !video) return;
        
        // Validate video source
        const source = video.querySelector('source');
        if (!source || !source.src) {
            console.warn('No valid source found for video');
            return;
        }

        // Add error handling for video
        video.addEventListener('error', function(e) {
            console.error('Video error:', e);
            // Show thumbnail and hide video on error
            thumbnail.style.display = 'block';
            video.style.display = 'none';
        });
        
        thumbnail.addEventListener('click', function() {
            thumbnail.style.display = 'none';
            video.style.display = 'block';
            
            if (video.paused) {
                video.play().catch(error => {
                    console.error('Video playback failed:', error);
                    thumbnail.style.display = 'block';
                    video.style.display = 'none';
                });
            }
        });

        // Reset video when it ends
        video.addEventListener('ended', function() {
            video.currentTime = 0;
            thumbnail.style.display = 'block';
            video.style.display = 'none';
        });
    });
});
