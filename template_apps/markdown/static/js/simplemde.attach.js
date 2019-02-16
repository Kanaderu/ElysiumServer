/*
$(document).ready(function() {
    $(".markdown .field-content textarea").each(function(index, elem) {
        var mde = new SimpleMDE({
            element: elem,
            autofocus: false
        });
        mde.render();
    });
});
*/
/*
 * Used to initialize Simple MDE when Markdown blocks are used in StreamFields
 */
function simplemdeAttach(id) {
        var mde = new SimpleMDE({
            element: document.getElementById(id),
            autofocus: false
        });
        mde.render();

        mde.codemirror.on("change", function(){
            $('#' + id).val(mde.value());
        });
}

/*
 * Used to initialize Simple MDE when MarkdownFields are used on a page.
 */
$(document).ready(function() {
    $(".object.markdown textarea").each(function(index, elem) {
        simplemdeAttach(elem.id);
    });
});