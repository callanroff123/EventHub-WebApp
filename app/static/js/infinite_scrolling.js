let currentPage = 1;
let isLoading = false;


function loadPosts() {
    if (isLoading) return;
    isLoading = true;
    let searchField = $("input[name='search-field']").val();
    let usersToggle = $("select[name='users_toggle']:checked").val();
    $.get({
        url: "{{ url_for('main.get_posts) }}",
        data: {
            page: page,
            search_field: searchField,
            users_toggle: usersToggle
        },
        success: function(data) {
            console.log(data);
            if (data.length > 0) {
                data.forEach(function(post) {
                    let postHTML = `
                        <table>
                            <tr>
                                <td width="50px">
                                    <a href="{{ url_for('main.profile', username=post.author) }}">
                                        <img src="${post.avatar}">
                                    </a>
                                </td>
                                <td>
                                    <a href="{{ url_for('main.profile', username=post.author) }}">
                                        ${post.author}
                                    </a>
                                    (<em>{{ _(moment(post.timestamp).fromNow()) }}</em>):
                                    <br>
                                    <span id="post${post.id}">
                                        ${post.body}
                                    </span>
                                    ${post.language !== '{{ g.locale }}' ? `
                                        <br>
                                        <span id="translation${post.id}">
                                            <a href="javascript:translate(
                                                'post${post.id}',
                                                'translation${post.id}',
                                                '${post.language}',
                                                '{{ g.locale }}'
                                            );">{{ _('Translate') }}</a>
                                        </span>` : ''}
                                </td>
                            </tr>
                        </table>
                        <br>
                    `;
                    $(".user-posts.activity").append(postHTML);
                });
                page++;
                isLoading = false;
            } else {
                $(window).off("scroll", onScroll);
            }
        }
    });
}


function resetPosts() {
    page = 1;  // Reset page number
    $("#post-list").empty();  // Clear current posts
    loadPosts();  // Load posts with new filters
}

// Trigger post reset when filter form changes
$("#post-filter-form").on("change", "input, select", function() {
    resetPosts();  // Reset and load posts on filter change
});

// Infinite scroll: Load more posts when user scrolls to bottom
$(window).on('scroll', function() {
    if ($(window).scrollTop() + $(window).height() >= $(document).height() - 100) {
        loadPosts();  // Load more posts when scrolled to the bottom
    }
});

// Load the initial set of posts when page loads
$(document).ready(function() {
    loadPosts();
});