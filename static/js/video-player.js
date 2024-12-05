document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing video players...');
    // Initialize Video.js players with enhanced error handling
    const videoPlayers = document.querySelectorAll('.video-js');
    const initializedPlayers = new Set();
    
    videoPlayers.forEach(player => {
        try {
            if (!player.id) {
                console.warn('Skipping player initialization: Missing ID');
                return;
            }

            // Check if player instance already exists
            if (videojs.getPlayers()[player.id]) {
                console.log(`Disposing existing player instance for ${player.id}`);
                videojs.getPlayers()[player.id].dispose();
            }
            
            const sourceElement = player.querySelector('source');
            if (!sourceElement || !sourceElement.src) {
                console.warn(`No valid source found for player ${player.id}`);
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
