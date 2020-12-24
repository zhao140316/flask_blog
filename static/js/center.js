/**
 * Created by 11314 on 2020/7/25.
 */
    // 设置富文本
    tinymce.init({
        selector: '.mytextarea',
        height: 600,
        plugins: "guickbars emoticons",
        inline: false,
        toolbar: true,
        menubar: true,
        quickbars_selection_toolbar: 'bold italic | link h2 h3 blockquote',
        quickbars_insert_toolbar: 'quickimage quicktable'
    });

    // 验证手机号码
