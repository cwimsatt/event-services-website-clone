document.addEventListener('DOMContentLoaded', function() {
    let masonry = null;
    const grid = document.querySelector('.gallery-grid');
    
    if (!grid) {
        console.warn('Gallery grid not found in the document');
        return;
    }
    
    // Handle errors gracefully
    const handleError = function(error) {
        console.error('Gallery initialization error:', error);
        // Fallback to basic grid layout if Masonry fails
        grid.style.display = 'grid';
        grid.style.gridTemplateColumns = 'repeat(auto-fill, minmax(300px, 1fr))';
        grid.style.gap = '1rem';
    };

    // Initialize Masonry with proper configuration and error handling
    const initMasonry = function() {
        try {
            if (typeof Masonry !== 'function') {
                throw new Error('Masonry library not loaded');
            }
            return new Masonry(grid, {
                itemSelector: '.gallery-item',
                columnWidth: '.gallery-item',
                percentPosition: true,
                transitionDuration: '0.3s'
            });
        } catch (error) {
            handleError(error);
            return null;
        }
    };

    // Initialize lightbox if GLightbox is available
    try {
        if (typeof GLightbox === 'function') {
            const lightbox = GLightbox({
                selector: '.glightbox',
                touchNavigation: true,
                loop: true,
                autoplayVideos: true
            });
        }
    } catch (error) {
        console.error('Error initializing lightbox:', error);
    }

    // Initialize filtering functionality
    const initializeFilters = function(masonryInstance) {
        try {
            const filterButtons = document.querySelectorAll('.filter-btn');
            const items = document.querySelectorAll('.gallery-item');
            
            if (!filterButtons.length) return;

            filterButtons.forEach(button => {
                button.addEventListener('click', function(e) {
                    e.preventDefault();
                    const category = this.getAttribute('data-category');
                    
                    if (!category) return;

                    // Update active button state
                    filterButtons.forEach(btn => btn.classList.remove('active'));
                    this.classList.add('active');

                    // Filter gallery items
                    items.forEach(item => {
                        if (category === 'all' || item.getAttribute('data-category') === category) {
                            item.style.display = '';
                            item.classList.add('show');
                        } else {
                            item.style.display = 'none';
                            item.classList.remove('show');
                        }
                    });

                    // Re-layout Masonry after filtering
                    if (masonryInstance && typeof masonryInstance.layout === 'function') {
                        setTimeout(() => {
                            masonryInstance.layout();
                        }, 100);
                    }
                });
            });
        } catch (error) {
            handleError(error);
        }
    };

    // Initialize lazy loading with Intersection Observer
    const initializeLazyLoading = function(masonryInstance) {
        try {
            const lazyImages = document.querySelectorAll('img.lazy');
            
            if (!lazyImages.length) return;

            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.classList.remove('lazy');
                            observer.unobserve(img);
                            
                            // Trigger layout update after image loads
                            img.addEventListener('load', () => {
                                if (masonryInstance && typeof masonryInstance.layout === 'function') {
                                    masonryInstance.layout();
                                }
                            });
                        }
                    }
                });
            }, {
                root: null,
                rootMargin: '50px',
                threshold: 0.1
            });

            lazyImages.forEach(img => imageObserver.observe(img));
        } catch (error) {
            handleError(error);
        }
    };

    // Initialize gallery with proper error handling
    const initializeGallery = () => {
        try {
            if (grid) {
                masonry = initMasonry();
                console.log('Masonry initialized successfully');
                initializeFilters(masonry);
                initializeLazyLoading(masonry);
            }
        } catch (error) {
            handleError(error);
        }
    };

    try {
        console.log('Initializing gallery with Masonry...');
        if (typeof Masonry !== 'function') {
            throw new Error('Masonry library not loaded');
        }

        // Check for imagesLoaded availability
        if (typeof imagesLoaded === 'function') {
            console.log('Using imagesLoaded for initialization');
            imagesLoaded(grid, function() {
                initializeGallery();
            });
        } else {
            console.warn('imagesLoaded not available, falling back to direct initialization');
            window.addEventListener('load', initializeGallery);
        }
    } catch (error) {
        console.error('Critical gallery initialization error:', error);
        handleError(error);
    }
});
