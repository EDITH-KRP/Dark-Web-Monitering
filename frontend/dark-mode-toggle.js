const darkModeToggle = document.getElementById('dark-mode-toggle');


if (localStorage.getItem('dark-mode') === 'true') {
    document.body.classList.add('dark-mode');
}


darkModeToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    
   
    const isDarkMode = document.body.classList.contains('dark-mode');
    localStorage.setItem('dark-mode', isDarkMode);
});
