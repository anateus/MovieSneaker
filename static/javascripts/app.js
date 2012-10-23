//noinspection BadExpressionStatementJS
(function ($, window, undefined) {
    var $doc = $(document),
        Modernizr = window.Modernizr;


    $.fn.foundationAlerts ? $doc.foundationAlerts() : null;
    $.fn.foundationAccordion ? $doc.foundationAccordion() : null;
    $.fn.foundationTooltips ? $doc.foundationTooltips() : null;
    $('input, textarea').placeholder();


    $.fn.foundationButtons ? $doc.foundationButtons() : null;


    $.fn.foundationNavigation ? $doc.foundationNavigation() : null;


    $.fn.foundationTopBar ? $doc.foundationTopBar() : null;

    $.fn.foundationCustomForms ? $doc.foundationCustomForms() : null;
    $.fn.foundationMediaQueryViewer ? $doc.foundationMediaQueryViewer() : null;


    $.fn.foundationTabs ? $doc.foundationTabs() : null;


    // UNCOMMENT THE LINE YOU WANT BELOW IF YOU WANT IE8 SUPPORT AND ARE USING .block-grids
    // $('.block-grid.two-up>li:nth-child(2n+1)').css({clear: 'both'});
    // $('.block-grid.three-up>li:nth-child(3n+1)').css({clear: 'both'});
    // $('.block-grid.four-up>li:nth-child(4n+1)').css({clear: 'both'});
    // $('.block-grid.five-up>li:nth-child(5n+1)').css({clear: 'both'});

    // Hide address bar on mobile devices
    if (Modernizr.touch) {
        $(window).load(function () {
            setTimeout(function () {
                window.scrollTo(0, 1);
            }, 0);
        });
    }

    var zipcode_pattern = /^\d{5}(-\d{4})?$/;

    function list_theatres(event) {
//        console.log(event);


        if (event != undefined && ( event.type=="click" || (event.type=="keyup" && event.which==13))) {
            $('#theatre_selection').removeClass('hidden');
            $('#theatre_list').html(''); // clear list
            var zipcode = $('#zipcode_box').val();
            if (zipcode_pattern.test(zipcode)) {
                $('#zipcode_error').addClass('hidden');
                $('#zipcode_box').removeClass('error');

                zipcode = zipcode.split('-')[0];

                $.ajax({
                    url:'/api/v1/venues',
                    type:'GET',
                    data:{ zipcode:zipcode },
                    dataType:'json'
                }).done(function (data, textStatus, jqXHR) {
                        var venueslength = data["venues"].length;

                        for (var i=0;i<venueslength; i++) {
                            $('#theatre_list').append(Mustache.render("<li><a href='#' class='theatre_link' theatre-id='{{ id }}'><strong>{{ name }}</strong><a/> - {{ address }}</li>",data["venues"][i]));


                        }
                });
            } else {
                $('#zipcode_error').removeClass('hidden');
                $('#zipcode_box').addClass('error');

            }

        }


    }

    function list_chains(event) {
        theatre_id = $(event.currentTarget).attr('theatre-id');
        $('#chains_display').removeClass('hidden');
        $('#chains_list').html(''); // clear list
        if (theatre_id) {
            $.ajax({
                url:'/api/v1/venues/'+theatre_id+'/chains',
                type:'GET',
                dataType:'json'
            }).done(function (data, textStatus, jqXHR) {
                    var chainslength = data["chains"].length;


                    for (var i=0;i<chainslength;i++) {
                        var chain = data["chains"][i];
                        console.log(chain);

                        var showings_html = "";

                        var chainlen = chain.length;
                        for (var j=0;j<chainlen;j++) {
                            showings_html+= Mustache.render("<span class='showing'><strong>{{ movie.name }}</strong> {{ start }} - {{ end }}</span>",chain[j][0]);

                        }
                        $('#chains_list').append(Mustache.render('<li class="chain">{{{ showings_html }}}</li>',{showings_html:showings_html}));
                    }


            });
        }

    }

    $('#list_theatres_button').live('click',list_theatres);
    $('#zipcode_box').live('keyup',list_theatres);
    $('#theatre_list a.theatre_link').live('click',list_chains);
})(jQuery, this);
