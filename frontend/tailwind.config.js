export default {
    content: ["./index.html", "./src/**/*.{ts,tsx}"],
    theme: {
        extend: {
            colors: {
                brand: {
                    ink: "#0f172a",
                    sky: "#1d4ed8",
                    mist: "#dbeafe",
                    pine: "#14532d",
                    warm: "#f8fafc",
                    danger: "#b91c1c"
                }
            },
            boxShadow: {
                card: "0 10px 30px rgba(15, 23, 42, 0.08)"
            }
        }
    },
    plugins: []
};
