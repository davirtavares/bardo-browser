module.exports = function(grunt) {

    grunt.initConfig({
        compass: {
            default: {
                options: {
                  sassDir: "sass",
                  cssDir: "css",
                  imagesDir: "img",
                  relativeAssets: true,
                  outputStyle: "expanded",
                },
            },
        },

        copy: {
            default: {
                files: [
                    {
                        expand: true,
                        cwd: "js/vendor/bootstrap-sass-official/assets/fonts",
                        src: ["**"],
                        dest: "fonts/",
                    },

                    {
                        expand: true,
                        cwd: "js/vendor/Font-Awesome/fonts",
                        src: ["**"],
                        dest: "fonts/",
                    },
                ],
            },
        },

        watch: {
            html: {
                files: [
                    "html/**/*"
                ],

                tasks: ["includereplace"],
            },

            sass: {
                files: [
                    "sass/**/*"
                ],

                tasks: ["compass"],
            },
        },

        includereplace: {
            default: {
                files: [
                    {
                        src: "**/*",
                        dest: "./",
                        expand: true,
                        cwd: "html",
                    },
                ],
            },
        },
    });

    grunt.loadNpmTasks("grunt-include-replace");
    grunt.loadNpmTasks("grunt-contrib-compass");
    grunt.loadNpmTasks("grunt-contrib-copy");
    grunt.loadNpmTasks("grunt-contrib-watch");

    grunt.registerTask("default", ["compass"]);

    grunt.registerTask("build", [
        "copy",
        "compass",
        "includereplace",
    ]);

};
