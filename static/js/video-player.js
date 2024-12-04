document.addEventListener('DOMContentLoaded', function() {
    // Initialize Video.js players
    const videoPlayers = document.querySelectorAll('.video-js');
    
    videoPlayers.forEach(player => {
        videojs(player.id, {
            controls: true,
            autoplay: false,
            preload: 'auto',
            responsive: true,
            fluid: true,
            playbackRates: [0.5, 1, 1.5, 2]
        });
    });

    // Custom video thumbnail overlay
    const videoThumbnails = document.querySelectorAll('.video-thumbnail');
    videoThumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', function() {
            const videoId = this.dataset.videoId;
            const player = videojs(videoId);
            
            this.style.display = 'none';
            player.play();
        });
    });
});
