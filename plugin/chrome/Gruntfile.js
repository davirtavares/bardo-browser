module.exports = function(grunt) {

    grunt.initConfig({
        prefix: "-brd-plugin-ns-"
    });

    grunt.config.merge({
        compass: {
            default: {
                options: {
                    sassDir: "sass",
                    cssDir: "build/css",
                    imagesDir: "img",
                    relativeAssets: true,
                    outputStyle: "expanded"
                }
            }
        },

        copy: {
            default: {
                files: [
                    {
                        expand: true,
                        cwd: "vendor/bootstrap-sass-official/assets/fonts",
                        src: ["**"],
                        dest: "build/fonts"
                    },

                    {
                        expand: true,
                        cwd: "vendor/Font-Awesome/fonts",
                        src: ["**"],
                        dest: "build/fonts"
                    },

                    {
                        expand: true,
                        src: ["icon.png", "manifest.json"],
                        dest: "build"
                    },

                    {
                        expand: true,
                        src: [
                            "vendor/jquery/dist/jquery.js",
                            "vendor/angular/angular.js",
                            "vendor/angular-route/angular-route.js",
                            "vendor/angular-bootstrap/ui-bootstrap-tpls.js"
                        ],
                        flatten: true,
                        dest: "build/js/3rdparty"
                    },

                    {
                        expand: true,
                        cwd: "js",
                        src: ["**"],
                        dest: "build/js"
                    },
                ]
            }
        },

        watch: {
            html: {
                files: [
                    "html/**/*"
                ],

                tasks: ["includereplace"]
            },

            sass: {
                files: [
                    "sass/**/*"
                ],

                tasks: ["compass"]
            }
        },

        includereplace: {
            default: {
                options: {
                    globals: {
                        "prefix": grunt.config("prefix")
                    }
                },

                files: [
                    {
                        src: "**/*",
                        dest: "build",
                        expand: true,
                        cwd: "html"
                    }
                ]
            }
        }
    });

    grunt.loadNpmTasks("grunt-include-replace");
    grunt.loadNpmTasks("grunt-contrib-compass");
    grunt.loadNpmTasks("grunt-contrib-copy");
    grunt.loadNpmTasks("grunt-contrib-watch");

    grunt.registerTask("prefix", function() {
        grunt.file.write("sass/_prefix.scss",
                '$prefix: "' + grunt.config("prefix") + '";\n');
    });

    grunt.registerTask("default", ["compass"]);

    grunt.registerTask("build", [
        "prefix",
        "copy",
        "compass",
        "includereplace"
    ]);

};
