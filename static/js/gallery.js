document.addEventListener('DOMContentLoaded', function() {
    // Initialize Masonry
    const grid = document.querySelector('.gallery-grid');
    
    if (!grid) return; // Exit if grid doesn't exist
    
    // Create a function to initialize Masonry
    const initMasonry = function() {
        const masonry = new Masonry(grid, {
            itemSelector: '.gallery-item',
            columnWidth: '.gallery-item',
            percentPosition: true
        });
        return masonry;
    };

    // Check if imagesLoaded is available
    if (typeof imagesLoaded === 'function') {
        imagesLoaded(grid, function() {
            const masonry = initMasonry();
        });
    } else {
        console.warn('imagesLoaded not available, initializing Masonry directly');
        const masonry = initMasonry();
    }

    // Initialize lightbox
            const lightbox = GLightbox({
                selector: '.glightbox',
                touchNavigation: true,
                loop: true,
                autoplayVideos: true
            });

            // Gallery filtering
            const filterButtons = document.querySelectorAll('.filter-btn');
            filterButtons.forEach(button => {
                button.addEventListener('click', function() {
                    const category = this.getAttribute('data-category');
                    
                    // Update active button state
                    filterButtons.forEach(btn => btn.classList.remove('active'));
                    this.classList.add('active');

                    // Filter gallery items
                    const items = document.querySelectorAll('.gallery-item');
                    items.forEach(item => {
                        const itemCategory = item.getAttribute('data-category');
                        if (category === 'all' || itemCategory === category) {
                            item.style.display = 'block';
                        } else {
                            item.style.display = 'none';
                        }
                    });

                    // Re-layout Masonry after filtering
                    masonry.layout();
                });
            });

            // Lazy loading for images
            const lazyImages = document.querySelectorAll('.lazy');
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        observer.unobserve(img);
                        masonry.layout(); // Re-layout after image loads
                    }
                });
            });

            lazyImages.forEach(img => imageObserver.observe(img));
        });
    }
});
