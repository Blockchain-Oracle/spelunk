const path = require("path");

// Builds the cockpit SPA into the Splunk app's static dir. React/ReactDOM are
// provided by Splunk Web (externals), same as the archived SUIT build.
// CSS (tokens) is copied verbatim, not inlined, so the view stylesheet attr
// can reference it directly.
module.exports = {
    entry: { cockpit: "./src/cockpit.tsx" },
    output: {
        path: path.resolve(
            __dirname,
            "../splunk_app/spelunk_app/appserver/static/spelunk"
        ),
        filename: "[name].js",
        clean: false,
    },
    resolve: { extensions: [".tsx", ".ts", ".js"] },
    module: {
        rules: [{ test: /\.tsx?$/, use: "ts-loader", exclude: /node_modules/ }],
    },
    externals: { react: "React", "react-dom": "ReactDOM" },
};
