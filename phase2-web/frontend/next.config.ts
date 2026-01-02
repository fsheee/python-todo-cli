import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Disable Turbopack for production builds (use Webpack)
  // This fixes path alias resolution in monorepo deployments
};

export default nextConfig;
