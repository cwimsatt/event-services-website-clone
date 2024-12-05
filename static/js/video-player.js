document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing video players...');
    
    // Validate videojs availability
    if (typeof videojs !== 'function') {
        console.error('Video.js library not loaded');
        return;
    }

    // Initialize Video.js players with enhanced error handling
    const videoPlayers = document.querySelectorAll('.video-js');
    const initializedPlayers = new Set();
    
    // Validate video source
    function validateVideoSource(sourceElement) {
        if (!sourceElement || !sourceElement.src) {
            return null;
        }
        
        // Check if the source file exists
        return new Promise((resolve) => {
            const xhr = new XMLHttpRequest();
            xhr.open('HEAD', sourceElement.src, true);
            xhr.onload = function() {
                resolve(xhr.status === 200 ? sourceElement.src : null);
            };
            xhr.onerror = function() {
                resolve(null);
            };
            xhr.send();
        });
    }
    
    // Cleanup existing players before initialization
    function cleanupExistingPlayer(playerId) {
        try {
            const existingPlayer = videojs.getPlayers()[playerId];
            if (existingPlayer) {
                existingPlayer.pause();
                existingPlayer.dispose();
                console.log(`Successfully disposed player: ${playerId}`);
            }
        } catch (error) {
            console.error(`Error disposing player ${playerId}:`, error);
        }
    }
    
    videoPlayers.forEach(async (player) => {
        try {
            if (!player.id) {
                console.warn('Skipping player initialization: Missing ID');
                return;
            }

            // Prevent duplicate initialization
            if (initializedPlayers.has(player.id)) {
                console.warn(`Player ${player.id} already initialized`);
                return;
            }

            // Cleanup existing player instance
            cleanupExistingPlayer(player.id);
            
            const sourceElement = player.querySelector('source');
            const validSource = await validateVideoSource(sourceElement);
            
            if (!validSource) {
                console.warn(`No valid source found for player ${player.id}`);
                // Show fallback content
                const fallbackMsg = document.createElement('div');
                fallbackMsg.className = 'video-fallback';
                fallbackMsg.innerHTML = '<p>Video unavailable</p>';
                player.parentNode.insertBefore(fallbackMsg, player);
                player.style.display = 'none';
                return;
            }
            
            console.log(`Initializing player: ${player.id}`);
            videojs(player.id, {
                controls: true,
                autoplay: false,
                preload: 'auto',
                responsive: true,
                fluid: true,
                playbackRates: [0.5, 1, 1.5, 2],
                sources: [{
                    src: sourceElement.src,
                    type: 'video/mp4'
                }]
            }).ready(function() {
                console.log(`Player ${player.id} initialized successfully`);
                initializedPlayers.add(player.id);
            });
        } catch (error) {
            console.error(`Error initializing video player ${player.id}:`, error);
        }
    });

    // Custom video thumbnail overlay with error handling
    const videoThumbnails = document.querySelectorAll('.video-thumbnail');
    videoThumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', function() {
            try {
                const videoId = this.dataset.videoId;
                if (!videoId) {
                    console.error('Missing video ID on thumbnail');
                    return;
                }

                const player = videojs(videoId);
                if (!player) {
                    console.error(`Player not found for ID: ${videoId}`);
                    return;
                }

                this.style.display = 'none';
                player.play();
            } catch (error) {
                console.error('Error playing video:', error);
            }
        });
    });
});
