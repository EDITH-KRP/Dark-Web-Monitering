document.addEventListener('DOMContentLoaded', () => {
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    
    // Since we're using a terminal theme, we're always in "dark mode" by default
    document.body.classList.add('dark-mode');
    
    // Set the toggle icon to a terminal-like symbol
    darkModeToggle.innerHTML = '<i class="fas fa-terminal"></i>';
    
    // Add transition class after initial load to prevent flash
    setTimeout(() => {
        document.documentElement.style.setProperty('--transition', 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)');
    }, 100);
    
    // Toggle between different terminal themes
    darkModeToggle.addEventListener('click', () => {
        // Add transition overlay
        const overlay = document.createElement('div');
        overlay.className = 'mode-transition-overlay';
        document.body.appendChild(overlay);
        
        // Toggle between different terminal themes
        document.body.classList.toggle('alt-terminal-theme');
        
        // Cycle through different terminal icons
        if (document.body.classList.contains('alt-terminal-theme')) {
            darkModeToggle.innerHTML = '<i class="fas fa-code"></i>';
        } else {
            darkModeToggle.innerHTML = '<i class="fas fa-terminal"></i>';
        }
        
        // Remove overlay with fade
        setTimeout(() => {
            overlay.style.opacity = '0';
            setTimeout(() => {
                overlay.remove();
            }, 300);
        }, 100);
        
        // Animate cards with a subtle transition effect instead of glitch
        document.querySelectorAll('.dashboard-card').forEach((card, index) => {
            setTimeout(() => {
                card.classList.add('pulse-effect');
                setTimeout(() => {
                    card.classList.remove('pulse-effect');
                }, 1000);
            }, index * 100);
        });
    });
    
    // Add overlay and glitch effect styles
    const style = document.createElement('style');
    style.textContent = `
        .mode-transition-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            z-index: 9998;
            opacity: 1;
            transition: opacity 0.3s ease;
            pointer-events: none;
        }
        
        .glitch-effect {
            animation: glitch 0.8s cubic-bezier(.25, .46, .45, .94) both;
        }
        
        .pulse-effect {
            animation: pulse 0.8s ease-in-out;
        }
        
        @keyframes pulse {
            0% {
                transform: scale(1);
                opacity: 1;
            }
            50% {
                transform: scale(1.02);
                opacity: 0.8;
            }
            100% {
                transform: scale(1);
                opacity: 1;
            }
        }
        
        @keyframes glitch {
            0% {
                transform: translate(0);
            }
            10% {
                transform: translate(-5px, 5px);
            }
            20% {
                transform: translate(-10px, -10px);
            }
            30% {
                transform: translate(5px, -5px);
            }
            40% {
                transform: translate(10px, 10px);
            }
            50% {
                transform: translate(-5px, 5px);
            }
            60% {
                transform: translate(-10px, -10px);
            }
            70% {
                transform: translate(5px, -5px);
            }
            80% {
                transform: translate(10px, 10px);
            }
            90% {
                transform: translate(-5px, 5px);
            }
            100% {
                transform: translate(0);
            }
        }
        
        .alt-terminal-theme {
            /* Swap colors - orange becomes primary, green becomes secondary */
            --primary-color: #ff9800;
            --primary-hover: #e68a00;
            --secondary-color: #39ff14;
            --secondary-hover: #32e612;
            --green-glow: 0 0 5px rgba(57, 255, 20, 0.3);
            --orange-glow: 0 0 5px rgba(255, 152, 0, 0.3);
        }
    `;
    document.head.appendChild(style);
});
