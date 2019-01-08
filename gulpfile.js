// Include and alias the following gulp packages
var
	gulp = require('gulp'),
	autoprefixer = require('gulp-autoprefixer'),
	del = require('del'),
	concat = require('gulp-concat'),
	cssmin = require('gulp-cssmin'),
	uglify = require('gulp-uglify'),
	sass = require('gulp-sass');

// Webroot path
var webroot = "./src/static/";

// Pre-compiled files
var preComp = "frontend/";

// Node modules path
var nodeModules = "node_modules/"

// Source, ignore (minified files), and output paths
var paths = {

	js: preComp + "js/*.js",
	css: preComp + "scss/*.scss",

	// All third party libraries CSS and JS should be added here
	bootstrapCss: nodeModules + "bootstrap/dist/css/bootstrap.min.css",
	bootstrapJs: nodeModules + "bootstrap/dist/js/bootstrap.min.js",

	fontAwesomeFonts: nodeModules + "font-awesome/fonts/",

	popperJs: nodeModules + "popper.js/dist/umd/popper.min.js",

	jqueryJs: nodeModules + "jquery/dist/jquery.min.js",

	jqueryValidation: nodeModules + "jquery-validation/dist/jquery.validate.min.js",

	// Output directories
	output: {
		css: webroot + "css/style.min.css",
		fonts: webroot + "fonts/",
		js: webroot + "js/scripts.min.js"
	}
}

// JS clean task (deletes scripts.min.js)
gulp.task("clean:js", function (cb) {
	del(paths.output.js, cb);
});

// CSS clean task (deletes style.min.css
gulp.task("clean:css", function (cb) {
	del(paths.output.css, cb);
});

// Combined clean task
gulp.task("clean", ["clean:js", "clean:css"]);

// JS min task
// jQuery --> Popper --> Bootstrap is the recommended sequence by Boostrap, do not change
gulp.task("min:js", function () {
	return gulp.src([paths.jqueryJs, paths.jqueryValidation, paths.popperJs, paths.bootstrapJs, paths.js])
		.pipe(concat(paths.output.js))
		.pipe(uglify())
		.pipe(gulp.dest("."));
});

// CSS min task
gulp.task("min:css", function () {
	return gulp.src([paths.bootstrapCss, paths.css])
		.pipe(concat(paths.output.css))
		.pipe(sass().on('error', sass.logError))
		.pipe(autoprefixer({
			browsers: ['last 2 versions'],
			cascade: false,
			remove: false
		}))
		.pipe(cssmin())
		.pipe(gulp.dest("."));
});

// Combined min task
gulp.task("min", ["min:js", "min:css"]);

gulp.task("fonts", function () {
	return gulp.src(paths.fontAwesomeFonts + "**")
		.pipe(gulp.dest(paths.output.fonts));
});

// Default (watch) task, watches for changes to any JS or CSS file and minifies on save
gulp.task("default", function () {
	gulp.watch([paths.js], ["clean:js", "min:js"]);
	gulp.watch([paths.css], ["clean:css", "min:css"]);
	gulp.watch(paths.fontAwesomeFonts, ["fonts"]);
});