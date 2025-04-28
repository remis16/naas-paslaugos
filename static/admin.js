// admin.js

// Kai puslapis užsikrauna
document.addEventListener('DOMContentLoaded', function() {
    // Sukuriam "Back to Top" mygtuko veikimą
    const backToTopButton = document.getElementById('backToTop');

    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            backToTopButton.style.display = 'block';
        } else {
            backToTopButton.style.display = 'none';
        }
    });

    backToTopButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // Fade-in efektas visam puslapiui (kad švelniai atsirastų)
    document.body.classList.add('visible');

    // Popup pranešimų valdymas (jei naudojami)
    const popup = document.getElementById('popup');
    if (popup) {
        popup.classList.add('show');
        setTimeout(() => {
            popup.style.opacity = '0';
            setTimeout(() => popup.remove(), 1000);
        }, 3000);
    }

    // Animacija, kai trinama paslauga (naudojama admin puslapyje)
    const deleteForms = document.querySelectorAll('form[action$="istrinti"]');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const li = this.closest('li');
            if (li) {
                li.style.transition = 'opacity 0.5s';
                li.style.opacity = '0.5';
            }
        });
    });
});
