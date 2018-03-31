
var pmScripts = inheritance(pmItems)

pmScripts.model.name = "scripts"
pmScripts.model.page_name = "script"
pmScripts.model.bulk_name = "script"
pmScripts.model.className = "pmScripts"


// show trang page list
pmScripts.model.page_list = {
    buttons: [
        {
            class: 'btn btn-primary',
            function: function () {
                return "spajs.open({ menuId:'new-" + this.model.page_name + "'}); return false;"
            },
            title: 'Create',
            link: function () {
                return '/?new-' + this.model.page_name
            },
        },
    ],
    title: "Scripts",
    short_title: "Script",
    fileds: [
        {
            title: 'Name',
            name: 'name',
        },
        {
            title: 'Lang',
            name: 'lang',
            class: function (item) {
                return 'class="hidden-xs"'
            },
        },
        {
            title: 'Project',
            name: 'project',
            value: function (item) {
                return item.project.name;
            },
            class: function (item) {
                return 'class="hidden-xs"'
            },
        },
        {
            title: 'Inventory',
            name: 'inventory',
            value: function (item) {
                return item.inventory.name;
            },
            class: function (item) {
                return 'class="hidden-xs"'
            },
        },
        {
            title: 'Date Create',
            name: 'date_created',
            value: function(item){
                return item.date_created
            },
            class: function (item) {
                return 'class="hidden-xs"'
            },
        }
    ],
    actions: [
        {
            class: 'btn btn-danger',
            function: function (item) {
                return 'spajs.showLoader(' + this.model.className + '.deleteItem(' + item.id + ')); return false;'
            },
            title: 'Delete',
            link: function () {
                return '#'
            }
        }
    ]
}

pmScripts.model.page_new = {
    title: "New host",
    short_title: "New host",
    fileds: pmHosts.fileds,
    sections: [
        function (section) {
            return jsonEditor.editor({}, {block: this.model.name});
        }
    ],
    onBeforeSave: function (data) {
        if (this.validateHostName(data.name)) {
            data.type = 'HOST'
        }
        else if (this.validateRangeName(data.name)) {
            data.type = 'RANGE'
        }
        else {
            $.notify("Error in host or range name", "error");
            return undefined;
        }

        data.vars = jsonEditor.jsonEditorGetValues()
        return data;
    },
    onCreate: function (result, status, xhr, callOpt) {
        var def = new $.Deferred();
        $.notify("Host created", "success");

        if (callOpt.parent_item) {
            if (callOpt.parent_type == 'group') {
                $.when(pmGroups.addSubHosts(callOpt.parent_item, [result.id])).always(function () {
                    $.when(spajs.open({menuId: "group/" + callOpt.parent_item})).always(function () {
                        def.resolve()
                    })
                })
            }
            else if (callOpt.parent_type == 'inventory') {
                $.when(pmInventories.addSubHosts(callOpt.parent_item, [result.id])).always(function () {
                    $.when(spajs.open({menuId: "inventory/" + callOpt.parent_item})).always(function () {
                        def.resolve()
                    })
                })
            }
            else if (callOpt.parent_type == 'project') {
                $.when(pmProjects.addSubHosts(callOpt.parent_item, [result.id])).always(function () {
                    $.when(spajs.open({menuId: "project/" + callOpt.parent_item})).always(function () {
                        def.resolve()
                    })
                })
            }
            else {
                console.error("Не известный parent_type", callOpt.parent_type)
                $.when(spajs.open({menuId: "host/" + result.id})).always(function () {
                    def.resolve()
                })
            }
        }
        else {
            $.when(spajs.open({menuId: "host/" + result.id})).always(function () {
                def.resolve()
            })
        }

        return def.promise();
    }
}

pmScripts.model.page_item = {

    buttons: [
        {
            class: 'btn btn-primary',
            function: function (item_id) {
                return 'spajs.showLoader(' + this.model.className + '.updateItem(' + item_id + '));  return false;'
            },
            title: 'Save',
            link: function () {
                return '#'
            },
        },
        {
            class: 'btn btn-default copy-btn',
            function: function (item_id) {
                return 'spajs.showLoader(' + this.model.className + '.copyAndEdit(' + item_id + '));  return false;'
            },
            title: '<span class="glyphicon glyphicon-duplicate" ></span>',
            link: function () {
                return '#'
            },
            help: 'Copy'
        },
        {
            class: 'btn btn-danger danger-right',
            function: function (item_id) {
                return 'spajs.showLoader(' + this.model.className + '.deleteItem(' + item_id + '));  return false;'
            },
            title: '<span class="glyphicon glyphicon-remove" ></span> <span class="hidden-sm hidden-xs" >Remove</span>',
            link: function () {
                return '#'
            },
        },
    ],
    sections: [],

    title: function (item_id) {
        return "Script " + pmScripts.model.items[item_id].justText('name')
    },
    short_title: function (item_id) {
        return pmScripts.model.items[item_id].justText('name', function (v) {
                return v.slice(0, 20)
            })
    },

    fileds: [
        [
            {
                filed: new filedsLib.filed.text(),
                title: 'Name',
                name: 'name',
                placeholder: 'Enter Script name',
                validator: function (value) {
                    return filedsLib.validator.notEmpty(value);
                },
                fast_validator: function (value) {
                    return value != '' && value
                }
            },
            {
                filed: new filedsLib.filed.disabled(),
                title: 'Lang',
                name: 'lang',
                placeholder: 'BASH/PYTHON',
            },
            {
                filed: new filedsLib.filed.disabled(),
                title: 'Date Created',
                name: 'date_created',

            },
            {
                filed: new filedsLib.filed.disabled(),
                title: 'Date Modified',
                name: 'date_modified',
            },
            {
                filed: new filedsLib.filed.disabled(),
                title: 'Inventory',
                name: 'inventory',
                placeholder: 'BASH/PYTHON',
            },
            {
                filed: new filedsLib.filed.text(),
                title: 'Script',
                name: 'script',
            },
            {
                filed: new filedsLib.filed.text(),
                title: 'Script',
                name: 'script',
            }

        ]
    ],
    onUpdate: function (result) {
        return true;
    },
    // onBeforeSave: function (data, item_id) {
    //     data.vars = jsonEditor.jsonEditorGetValues()
    //     if (this.validateHostName(data.name)) {
    //         data.type = 'HOST'
    //     }
    //     else if (this.validateRangeName(data.name)) {
    //         data.type = 'RANGE'
    //     }
    //     else {
    //         $.notify("Error in host or range name", "error");
    //         return undefined;
    //     }
    //     return data;
    // },
}

pmScripts.copyItem = function (item_id) {
    var def = new $.Deferred();
    var thisObj = this;

    $.when(this.loadItem(item_id)).done(function () {
        var data = thisObj.model.items[item_id];
        $.when(encryptedCopyModal.replace(data)).done(function (data) {
            delete data.id;
            spajs.ajax.Call({
                url: "/api/v1/" + thisObj.model.name + "/",
                type: "POST",
                contentType: 'application/json',
                data: JSON.stringify(data),
                success: function (data) {
                    thisObj.model.items[data.id] = data
                    def.resolve(data.id)
                },
                error: function (e) {
                    def.reject(e)
                }
            });
        }).fail(function (e) {
            def.reject(e)
        })

    }).fail(function (e) {
        def.reject(e)
    })


    return def.promise();
}

tabSignal.connect("polemarch.start", function () {

    // gọi api get all script
    spajs.addMenu({
        id: "scripts",
        urlregexp: [/^scripts$/, /^script$/, /^scripts\/search\/?$/, /^scripts\/page\/([0-9]+)$/],
        onOpen: function (holder, menuInfo, data) {
            return pmScripts.showList(holder, menuInfo, data);

        }
    })

    // gọi api get detail script
    spajs.addMenu({
        id: "script",
        urlregexp: [/^scripts\/([0-9]+)$/, /^script\/([0-9]+)$/],
        onOpen: function (holder, menuInfo, data) {
            return pmScripts.showItem(holder, menuInfo, data);
        }
    })

})

//изменение типа input'a на file при выборе