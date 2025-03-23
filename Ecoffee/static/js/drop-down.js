//dropdown menu
document.addEventListener('DOMContentLoaded', function() {
    const userMenu = document.querySelector('.user-menu');
    const dropdown = document.querySelector('.dropdown-menu');
  
    userMenu.addEventListener('click', function(e) {
        e.stopPropagation();
        dropdown.classList.toggle('show');
    });
  
    document.addEventListener('click', function() {
        dropdown.classList.remove('show');
    });
  
    dropdown.addEventListener('click', function(e) {
        e.stopPropagation();
    });
  });

