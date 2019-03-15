/*
document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('.parallax');
    var instances = M.Parallax.init(elems, options);
});
*/
// Or with jQuery
$(document).ready(function(){
    // Set parallax
    $('.parallax').parallax();

    // Scroll to #top
    $('html, body').animate({
        scrollTop: $('#top').offset().top
    }, 'slow');

    // Initial parallax image resize
    var images = document.querySelectorAll('.parallax-container');
    images.forEach(function(image){
        image.style.height = window.innerHeight + 'px';
    });

    // Resize parallax images on window resize
    window.addEventListener("resize", resize_function);
    function resize_function() {
        var images = document.querySelectorAll('.parallax-container');
        images.forEach(function(image){
            image.style.height = window.innerHeight + 'px';
        });
    }

    // Video Controls
    $('[id|="state"]').on('click', function () {
        var video = $(this).parent().children('video#video').get(0);
        var icons = $(this).children('span');
        //$('.parallax-container').toggleClass('fade');
        //$(this).toggleClass('fade')

        //$(this).parent().toggleClass('fade');
        if (video.paused) {
            video.play();
            icons.removeClass('fa-play').addClass('fa-pause');
        } else {
            video.pause();
            icons.removeClass('fa-pause').addClass('fa-play');
        }
    });

});