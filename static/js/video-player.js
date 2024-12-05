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
            return false;
        }
        
        const validTypes = ['video/mp4', 'video/webm', 'video/ogg'];
        return validTypes.includes(sourceElement.type);
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
            const validSource = validateVideoSource(sourceElement);
            
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
            
            const playerOptions = {
                controls: true,
                autoplay: false,
                preload: 'auto',
                responsive: true,
                fluid: true,
                sources: [{
                    src: sourceElement.src,
                    type: sourceElement.type || 'video/mp4'
                }]
            };
            
            if (!videojs.getPlayers()[player.id]) {
                videojs(player.id, playerOptions, function() {
                    console.log(`Player ${player.id} initialized successfully`);
                    initializedPlayers.add(player.id);
                });
            }
        } catch (error) {
            console.error(`Error initializing video player ${player.id}:`, error);
            showVideoFallback(player);
        }
    });

    function showVideoFallback(player) {
        const fallbackMsg = document.createElement('div');
        fallbackMsg.className = 'video-fallback';
        fallbackMsg.innerHTML = '<p>Error loading video</p>';
        player.parentNode.insertBefore(fallbackMsg, player);
        player.style.display = 'none';
    }

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
                player.play().catch(error => {
                    console.error('Error playing video:', error);
                    this.style.display = 'block';
                });
            } catch (error) {
                console.error('Error handling thumbnail click:', error);
                this.style.display = 'block';
            }
        });
    });
});
