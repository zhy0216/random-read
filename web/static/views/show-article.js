define(['jquery', 'underscore', 'backbone', 'views/pageview'], function($, _, backbone, PageView) {
    'use strict';

    var ShowArticle = PageView.extend({
        events: {
            'click .toolbar .btn.star': 'unstar',
            'click .toolbar .btn.unstar': 'star',
            'click .toolbar .btn.archive': 'archive',
        },
        template: _.template($("#article-shower-template").html()),
        star: function() {
            this.model.star();
        },
        unstar: function() {
            this.model.unstar();
        },
        archive: function(e) {
            this.model.archive().done(function(data) {
                Backbone.trigger("require-login", data);
                if(data.ok){
                    Backbone.trigger("url-navigate", "random-walk", {trigger: true});
                }
            });
        },
        render: function(){
            this.$el.html(this.template(this.model));
            this.undelegateEvents();
            this.delegateEvents();
        }
    })

    return ShowArticle;
})