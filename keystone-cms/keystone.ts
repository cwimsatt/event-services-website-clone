import { config, list } from '@keystone-next/keystone/schema';
import { text, timestamp, image, file, relationship } from '@keystone-next/fields';
import { createAuth } from '@keystone-next/auth';

const { withAuth } = createAuth({
  listKey: 'User',
  identityField: 'email',
  secretField: 'password',
  initFirstItem: {
    fields: ['name', 'email', 'password'],
  },
});

const Event = list({
  fields: {
    title: text({ isRequired: true }),
    description: text({ isRequired: true, ui: { displayMode: 'textarea' } }),
    image: image({
      storage: 'local_images',
    }),
    video: file({
      storage: 'local_videos',
    }),
    category: relationship({ ref: 'Category', many: false }),
    date: timestamp(),
  },
});

const Category = list({
  fields: {
    name: text({ isRequired: true }),
    slug: text({ isRequired: true, isUnique: true }),
    description: text({ ui: { displayMode: 'textarea' } }),
    events: relationship({ ref: 'Event', many: true }),
  },
});

export default withAuth(
  config({
    server: {
      cors: {
        origin: process.env.FRONTEND_URL || 'http://localhost:5000',
        credentials: true,
      },
    },
    db: {
      provider: 'postgresql',
      url: process.env.DATABASE_URL,
      onConnect: async context => {
        console.log('Connected to database');
      },
    },
    lists: {
      Event,
      Category,
    },
    ui: {
      isAccessAllowed: context => !!context.session?.data,
    },
    storage: {
      local_images: {
        kind: 'local',
        type: 'image',
        storagePath: 'public/images',
        serverRoute: {
          path: 'images',
        },
        generateUrl: path => `/images${path}`,
      },
      local_videos: {
        kind: 'local',
        type: 'file',
        storagePath: 'public/videos',
        serverRoute: {
          path: 'videos',
        },
        generateUrl: path => `/videos${path}`,
      },
    },
  })
);
