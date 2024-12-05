document.addEventListener('DOMContentLoaded', function() {
    const grid = document.querySelector('.gallery-grid');
    
    if (!grid) {
        console.warn('Gallery grid not found in the document');
        return;
    }
    
    // Initialize Masonry layout
    const initializeMasonry = function() {
        console.log('Initializing gallery with Masonry...');
        try {
            if (typeof Masonry !== 'function') {
                throw new Error('Masonry library not loaded');
            }

            const masonry = new Masonry(grid, {
                itemSelector: '.gallery-item',
                columnWidth: '.gallery-item',
                percentPosition: true,
                transitionDuration: '0.3s'
            });

            console.log('Masonry initialized successfully');
            return masonry;
        } catch (error) {
            console.error('Gallery initialization error:', error);
            // Fallback to basic grid layout
            grid.style.display = 'grid';
            grid.style.gridTemplateColumns = 'repeat(auto-fill, minmax(300px, 1fr))';
            grid.style.gap = '1rem';
            return null;
        }
    };

    // Initialize filtering functionality
    const initializeFilters = function(masonry) {
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
                if (masonry) {
                    setTimeout(() => masonry.layout(), 100);
                }
            });
        });
        console.log('Filters initialized');
    };

    // Initialize lazy loading
    const initializeLazyLoading = function(masonry) {
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
                        
                        // Update layout after image loads
                        img.addEventListener('load', () => {
                            if (masonry) {
                                masonry.layout();
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
        console.log('Lazy loading initialized');
    };

    // Wait for images to load before initializing
    if (typeof imagesLoaded === 'function') {
        console.log('Using imagesLoaded for initialization');
        imagesLoaded(grid, function() {
            const masonry = initializeMasonry();
            if (masonry) {
                initializeFilters(masonry);
                initializeLazyLoading(masonry);
            }
        });
    } else {
        console.warn('imagesLoaded not available, falling back to direct initialization');
        const masonry = initializeMasonry();
        if (masonry) {
            initializeFilters(masonry);
            initializeLazyLoading(masonry);
        }
    }
});
