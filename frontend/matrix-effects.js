// Matrix-like background effects
document.addEventListener('DOMContentLoaded', () => {
    // Create matrix rain effect
    createMatrixRain();
    
    // Add random glitch effects to elements
    addRandomGlitchEffects();
});

// Create matrix digital rain
function createMatrixRain() {
    const matrixBackground = document.querySelector('.matrix-background');
    
    // Create canvas for matrix rain
    const canvas = document.createElement('canvas');
    canvas.className = 'matrix-canvas';
    canvas.style.position = 'absolute';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.opacity = '0.03'; // Reduced opacity for better text visibility
    canvas.style.zIndex = '-10'; // Ensure it's well below content
    
    matrixBackground.appendChild(canvas);
    
    // Set canvas size
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    // Get canvas context
    const ctx = canvas.getContext('2d');
    
    // Characters to use in the matrix rain
    const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
    
    // Set font size and calculate columns
    const fontSize = 14;
    const columns = Math.floor(canvas.width / fontSize);
    
    // Array to track the y position of each column
    const drops = [];
    for (let i = 0; i < columns; i++) {
        drops[i] = Math.random() * -100;
    }
    
    // Draw the matrix rain
    function draw() {
        // Set semi-transparent black background to create trail effect
        ctx.fillStyle = 'rgba(10, 14, 23, 0.1)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Set text color and font to neon green
        ctx.fillStyle = '#39ff14';
        ctx.font = `${fontSize}px monospace`;
        
        // Draw characters
        for (let i = 0; i < drops.length; i++) {
            // Get random character
            const char = chars[Math.floor(Math.random() * chars.length)];
            
            // Draw character
            ctx.fillText(char, i * fontSize, drops[i] * fontSize);
            
            // Move drop down
            drops[i]++;
            
            // Reset drop to top with random delay when it reaches bottom
            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }
        }
    }
    
    // Update canvas size on window resize
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        
        // Recalculate columns
        const newColumns = Math.floor(canvas.width / fontSize);
        
        // Adjust drops array
        if (newColumns > drops.length) {
            // Add new columns
            for (let i = drops.length; i < newColumns; i++) {
                drops[i] = Math.random() * -100;
            }
        } else if (newColumns < drops.length) {
            // Remove excess columns
            drops.length = newColumns;
        }
    });
    
    // Start animation
    setInterval(draw, 50);
}

// Add random glitch effects to elements - but only to cards, not headings
function addRandomGlitchEffects() {
    // Elements that can have glitch effects - ONLY dashboard cards, no headings
    const glitchableElements = document.querySelectorAll('.dashboard-card');
    
    // Add glitch effect to random element every 10-20 seconds (very infrequent)
    setInterval(() => {
        // Select random element
        const randomIndex = Math.floor(Math.random() * glitchableElements.length);
        const element = glitchableElements[randomIndex];
        
        // Add glitch class
        element.classList.add('glitch-effect');
        
        // Remove glitch class after animation
        setTimeout(() => {
            element.classList.remove('glitch-effect');
        }, 600); // Very short duration
    }, Math.random() * 10000 + 10000); // Very infrequent
}