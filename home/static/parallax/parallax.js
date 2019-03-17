// Set parallax on images using Materialize
document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('.parallax');
    var instances = M.Parallax.init(elems);
});

$(document).ready(function(){
    /*
    // Set parallax on videos
    $(window).on('load scroll', function () {
        var scrolled = $(this).scrollTop();
        // set on title tags
        $('#title').css({
            'transform': 'translate3d(0, ' + -(scrolled * 0.2) + 'px, 0)', // parallax (20% scroll rate)
            'opacity': 1 - scrolled / 400 // fade out at 400px from top
        });
        // set on video tags
        $('#video').css('transform', 'translate3d(0, ' + -(scrolled * 0.50) + 'px, 0)'); // parallax (25% scroll rate)
    });
    */
    // Set parallax on videos
    $(window).on('load scroll', function () {
        var scrolled = $(this).scrollTop();
        // set on video tags
        $('#video').parent().css('transform', 'translate3d(0, ' + -(scrolled * 0.25) + 'px, 0)'); // parallax (25% scroll rate)
    });

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