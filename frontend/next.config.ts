import type { NextConfig } from "next";

const djangoApiBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${djangoApiBaseUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
