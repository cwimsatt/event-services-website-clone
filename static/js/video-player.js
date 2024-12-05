document.addEventListener('DOMContentLoaded', function() {
    const initializeVideoPlayers = function() {
        console.log('Initializing video players...');
        const videoContainers = document.querySelectorAll('.video-container');
        
        videoContainers.forEach((container, index) => {
            const thumbnail = container.querySelector('.video-thumbnail');
            const video = container.querySelector('video');
            const playerId = `video-${index}`;
            
            if (!thumbnail || !video) return;
            
            // Set unique ID for the video element
            video.id = playerId;
            
            // Validate video source
            const source = video.querySelector('source');
            if (!source || !source.src) {
                console.warn('No valid source found for player', playerId);
                return;
            }

            // Initialize video player
            try {
                // Clean up existing player instance if it exists
                if (videojs.getPlayer(playerId)) {
                    console.log('Successfully disposed player:', playerId);
                    videojs.getPlayer(playerId).dispose();
                }

                // Initialize new player
                const player = videojs(playerId, {
                    controls: true,
                    preload: 'none',
                    fluid: true,
                    playsinline: true
                });

                // Add error handling
                player.on('error', function(e) {
                    console.error('Video error:', e);
                    thumbnail.style.display = 'block';
                    video.style.display = 'none';
                });

                // Handle thumbnail click
                thumbnail.addEventListener('click', function() {
                    thumbnail.style.display = 'none';
                    video.style.display = 'block';
                    player.play().catch(error => {
                        console.error('Video playback failed:', error);
                        thumbnail.style.display = 'block';
                        video.style.display = 'none';
                    });
                });

                // Reset to thumbnail when video ends
                player.on('ended', function() {
                    player.currentTime(0);
                    thumbnail.style.display = 'block';
                    video.style.display = 'none';
                });

            } catch (error) {
                console.error('Error initializing video player', playerId + ':', error);
                // Ensure thumbnail remains visible on error
                if (thumbnail) thumbnail.style.display = 'block';
                if (video) video.style.display = 'none';
            }
        });
    };

    // Initialize video players
    initializeVideoPlayers();
});
