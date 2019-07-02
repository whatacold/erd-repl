// Model and View definitions
var ErdModel = Backbone.Model.extend({
    urlRoot: "/erds/",

    defaults: {
        id: '',
        sourceCode: '',
        imageUri: '',
    },

    initialize: function() {
        this.fetch();
    }
});

var AppView = Backbone.View.extend({
    el: "#app-view",
    events: {
        "click #preview": "onPreviewClicked",
    },

    onPreviewError: function(model, response, options) {
        this.$('.alert').text(response.responseJSON.error).show();
    },

    onPreviewClicked: function() {
        this.$('.alert').hide();
        erdModel.save({sourceCode: $("#source-code-textarea").val()},  // XXX .text() not work, so use .val()
                      {error: this.onPreviewError}); // compile it XXX 2 views tangled
    },
});

var ErdView = Backbone.View.extend({
    el: "#erd-view",

    initialize: function() {
        this.listenTo(this.model, "change", this.render);
    },

    template: _.template($("#template-erd-view").html()),
    render: function() { // reload image
        this.$el.html(this.template(this.model.attributes));
    }
});
