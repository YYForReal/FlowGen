/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_BASE_URL}:path*`, // 代理到后端 API 服务器
      },
    ];
  },
  images: {
    domains: ['www.plantuml.com'],
  },
  async headers() {
    return [
      {
        source: '/drawio/:path*',
        headers: [
          {
            key: 'Access-Control-Allow-Origin',
            value: '*',
          },
        ],
      },
    ];
  },
};
module.exports = nextConfig;