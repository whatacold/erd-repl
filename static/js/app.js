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
    tagName: "body",
    events: "",

    onPreviewClicked: function() {
        console.log("in preview")
        erdModel.save(); // let it compile,  // XXX 2 views tangled
    }
});

var ErdView = Backbone.View.extend({
    el: "#erd-view",

    initialize: function() {
        this.listenTo(this.model, "change", this.render);
    },

    template: _.template($("#template-erd-view").html()),
    render: function() { // reload image
        console.log("render erd view...");
        this.$el.html(this.template(this.model.attributes));
    }
});