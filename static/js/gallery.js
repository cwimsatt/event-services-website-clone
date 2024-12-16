document.addEventListener('DOMContentLoaded', function() {
    // Only initialize gallery on pages that have the gallery-grid
    const grid = document.querySelector('.gallery-grid');
    if (!grid) {
        console.log('No gallery grid found - skipping initialization');
        return;
    }
    
    console.log('Gallery grid found, initializing...');
    
    // Initialize Masonry layout for multiple grids
    const initializeMasonry = function() {
        console.log('Initializing gallery with Masonry...');
        const grids = document.querySelectorAll('.gallery-grid');
        const masonryInstances = [];

        grids.forEach((grid, index) => {
            try {
                if (typeof Masonry !== 'function') {
                    throw new Error('Masonry library not loaded');
                }

                console.log(`Initializing Masonry for grid ${index + 1}`);
                const masonry = new Masonry(grid, {
                    itemSelector: '.gallery-item',
                    columnWidth: '.gallery-item',
                    gutter: 20,
                    fitWidth: true,
                    transitionDuration: '0.3s'
                });

                masonryInstances.push(masonry);
                if (masonry && typeof masonry.layout === 'function') {
                    masonry.layout();
                }
                console.log(`Masonry initialized successfully for grid ${index + 1}`);
            } catch (error) {
                console.error(`Gallery initialization error for grid ${index + 1}:`, error);
                // Fallback to basic flex layout
                grid.style.display = 'flex';
                grid.style.flexWrap = 'wrap';
                grid.style.justifyContent = 'space-between';
            }
        });

        return masonryInstances;
    };

    // Initialize filtering functionality
    const initializeFilters = function(masonryInstances) {
        const filterButtons = document.querySelectorAll('.filter-btn');
        
        if (!filterButtons.length) return;

        filterButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const category = this.getAttribute('data-category');
                
                if (!category) return;

                // Update active button state
                filterButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');

                // Destroy existing Masonry instances
                if (masonryInstances && masonryInstances.length) {
                    masonryInstances.forEach(masonry => {
                        if (masonry && masonry.destroy) {
                            masonry.destroy();
                        }
                    });
                }

                // Wait for DOM updates
                setTimeout(() => {
                    // Reinitialize Masonry
                    const newMasonryInstances = initializeMasonry();
                    
                    // Update layout after a short delay to ensure proper positioning
                    setTimeout(() => {
                        newMasonryInstances.forEach(masonry => {
                            if (masonry && masonry.layout) {
                                masonry.layout();
                            }
                        });
                    }, 100);
                }, 100);
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
    const grids = document.querySelectorAll('.gallery-grid');
    if (!grids.length) {
        console.log('No gallery grids found - skipping initialization');
        return;
    }

    if (typeof imagesLoaded === 'function') {
        console.log('Using imagesLoaded for initialization');
        imagesLoaded(grids, function() {
            const masonryInstances = initializeMasonry();
            initializeFilters(masonryInstances);
            initializeLazyLoading(masonryInstances);
        });
    } else {
        console.warn('imagesLoaded not available, falling back to direct initialization');
        const masonryInstances = initializeMasonry();
        initializeFilters(masonryInstances);
        initializeLazyLoading(masonryInstances);
    }
});