document.addEventListener('DOMContentLoaded', function() {
    const videoContainers = document.querySelectorAll('.video-container');
    
    videoContainers.forEach(container => {
        const thumbnail = container.querySelector('.video-thumbnail');
        const video = container.querySelector('video');
        
        if (!thumbnail || !video) return;
        
        thumbnail.addEventListener('click', function() {
            // Simple show/hide toggle
            thumbnail.style.display = 'none';
            video.style.display = 'block';
            
            // Basic play functionality
            if (video.paused) {
                video.play().catch(error => {
                    console.log('Video playback failed:', error);
                    thumbnail.style.display = 'block';
                    video.style.display = 'none';
                });
            }
        });
    });
});