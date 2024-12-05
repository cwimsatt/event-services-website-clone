document.addEventListener('DOMContentLoaded', function() {
    // Initialize Video.js players with error handling
    const videoPlayers = document.querySelectorAll('.video-js');
    const initializedPlayers = new Set();
    
    videoPlayers.forEach(player => {
        try {
            if (!player.id || initializedPlayers.has(player.id)) {
                console.warn(`Skipping player initialization: ${player.id ? 'Already initialized' : 'Missing ID'}`);
                return;
            }
            
            videojs(player.id, {
                controls: true,
                autoplay: false,
                preload: 'auto',
                responsive: true,
                fluid: true,
                playbackRates: [0.5, 1, 1.5, 2]
            }, function() {
                console.log(`Player ${player.id} initialized successfully`);
            });
            
            initializedPlayers.add(player.id);
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
