// Build the site's Google Ads campaign as Google Ads Editor import files.
//
//   npm run ads:build
//
// Inputs: the resorts in src/resorts.ts with their trail counts
// (src/data/resorts/<id>/trails.ts), and the campaign below: settings, ad
// text, keywords, negatives and assets. Output: editor/1-campaigns.csv ...
// editor/9-structured-snippets.csv, numbered in import order (README.md,
// "Importing"), and preview.md, every ad and keyword for reading.
//
// Every text is checked against Google's limits before anything is written
// (headlines 30 characters, descriptions 90, display paths 15, sitelink text
// 25 and its descriptions 35, callouts and snippet values 25); where a line
// lists alternatives, the first that fits is used. A negative keyword that
// would block one of its own campaign's keywords stops the build, and so does
// a resort in src/resorts.ts without an entry in RESORT_ADS, so a new resort
// can't be left out of the campaign.
import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { RESORTS } from '../../src/resorts.ts';

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT = join(HERE, 'editor');
const SITE = 'https://www.myskiruns.app/';

// ---------------------------------------------------------------- settings
// What the CSVs can't set (location option, AI Max, automatically created
// assets, EU political ads) is set by hand: README.md, "Settings".

const EAST = new Set(['Vermont', 'New York', 'New Hampshire', 'Maine']);
// states and provinces east to west, for lists in ads (others go last)
const REGION_ORDER = ['Vermont', 'New York', 'New Hampshire', 'Maine', 'Colorado', 'Montana', 'Utah', 'California', 'Oregon',
  'British Columbia'];

const CAMPAIGNS = [
  // resort trail-map searches in Vermont, New York, New Hampshire and Maine;
  // French too: Quebec skiers fill Jay Peak, Stowe and the rest
  { key: 'east', name: 'Trail Maps - East', budget: 5, cpcLimit: 1, languages: 'en;fr' },
  // Colorado, Montana, Utah, California, Oregon and British Columbia
  { key: 'west', name: 'Trail Maps - West', budget: 5, cpcLimit: 1, languages: 'en' },
  // people looking for a way to track their runs, at any resort
  { key: 'tracker', name: 'Ski Run Tracker', budget: 5, cpcLimit: 1.5, languages: 'en' },
];

const LOCATIONS = [
  { id: 2840, name: 'United States' },
  { id: 2124, name: 'Canada' },
];

// ------------------------------------------------------------ resort ads
// short: the resort's name in tight headlines ("Ski Every Run at Smuggs").
// path: display path 1 (myskiruns.app/<path>/Trail-Map).
// area: a headline about the resort's own terrain, from its trail list.
// names: what people call the resort when it can't mean anything else; the
//   first gets the full keyword set (keywordsFor), the rest "<name> trail map"
//   and "<name> ski map".
// keywords: more, as [text, 'exact' | 'phrase']; ambiguous bare names
//   ("keystone", "park city") only as exact "trail map" searches, which a
//   winter campaign mostly gets from skiers.
// negatives: other things the names mean (towns, parks, roads, hikes).
const RESORT_ADS = {
  killington: {
    short: 'Killington',
    path: 'Killington',
    area: 'Skye Peak to Bear Mountain',
    names: ['killington'],
    negatives: ['pico', 'long trail', 'appalachian trail', 'bucklin'],
  },
  stowe: {
    short: 'Stowe',
    path: 'Stowe',
    area: 'Mt. Mansfield & Spruce Peak',
    names: ['stowe', 'stowe mountain'],
    negatives: ['recreation path', 'rec path', 'cady hill', 'adams camp'],
  },
  okemo: {
    short: 'Okemo',
    path: 'Okemo',
    area: 'Okemo and Jackson Gore',
    names: ['okemo'],
  },
  sugarbush: {
    short: 'Sugarbush',
    path: 'Sugarbush',
    area: 'Lincoln Peak & Mt. Ellen',
    names: ['sugarbush'],
    negatives: ['farm', 'maple', 'sugarhouse', 'sugaring'],
  },
  'jay-peak': {
    short: 'Jay Peak',
    path: 'Jay-Peak',
    area: 'Jay Peak Trails and Glades',
    names: ['jay peak'],
    negatives: ['pump house', 'long trail'],
  },
  'smugglers-notch': {
    short: 'Smuggs',
    path: 'Smugglers-Notch',
    area: 'Morse, Madonna & Sterling',
    names: ['smugglers notch', 'smuggs'],
    negatives: ['state park', 'road', 'pass', 'boulders', 'cave', 'campground'],
  },
  whiteface: {
    short: 'Whiteface',
    path: 'Whiteface',
    area: "Lake Placid's Whiteface",
    names: ['whiteface', 'whiteface mountain'],
    negatives: ['highway', 'toll', 'castle', 'new hampshire', 'nh'],
  },
  hunter: {
    short: 'Hunter',
    path: 'Hunter-Mountain',
    area: 'Hunter in the Catskills',
    names: ['hunter mountain'],
    negatives: ['fire tower', 'spruceton', 'devils path'],
  },
  wildcat: {
    short: 'Wildcat',
    path: 'Wildcat',
    area: 'Wildcat at Pinkham Notch',
    names: ['wildcat mountain'],
    keywords: [
      ['wildcat ski map', 'phrase'],
      ['wildcat ski trails', 'phrase'],
    ],
    negatives: ['wisconsin', 'state park', 'canyon', 'oregon', 'california'],
  },
  'sunday-river': {
    short: 'Sunday River',
    path: 'Sunday-River',
    area: "Maine's Sunday River",
    names: ['sunday river'],
  },
  sugarloaf: {
    short: 'Sugarloaf',
    path: 'Sugarloaf',
    area: 'Including the Snowfields',
    names: ['sugarloaf maine', 'sugarloaf mountain maine', 'sugarloaf resort'],
    keywords: [
      ['sugarloaf trail map', 'exact'],
      ['sugarloaf ski map', 'exact'],
      ['sugarloaf ski map', 'phrase'],
      ['sugarloaf ski trails', 'phrase'],
    ],
    negatives: [
      'maryland', 'md', 'rio', 'brazil', 'key', 'keys', 'florida', 'state park', 'ridge',
      'wisconsin', 'michigan', 'pennsylvania', 'california', 'australia',
    ],
  },
  vail: {
    short: 'Vail',
    path: 'Vail',
    area: 'Back Bowls & Blue Sky Basin',
    names: ['vail'],
    keywords: [
      ['vail back bowls map', 'phrase'],
      ['vail front side map', 'phrase'],
      ['blue sky basin map', 'phrase'],
    ],
    negatives: ['arizona', 'az', 'vail pass', 'vail lake', 'temecula', 'stock', 'investor'],
  },
  breckenridge: {
    short: 'Breckenridge',
    path: 'Breckenridge',
    area: 'Peaks 6 Through 10',
    names: ['breckenridge', 'breck'],
    negatives: ['texas', 'tx', 'minnesota', 'mn', 'michigan', 'distillery', 'town map'],
  },
  keystone: {
    short: 'Keystone',
    path: 'Keystone',
    area: 'Dercum, North Peak, Outback',
    names: ['keystone resort', 'keystone colorado'],
    keywords: [
      ['keystone trail map', 'exact'],
      ['keystone ski map', 'exact'],
      ['keystone ski map', 'phrase'],
      ['keystone ski trails', 'phrase'],
    ],
    negatives: [
      'south dakota', 'sd', 'rushmore', 'state park', 'pennsylvania', 'pa', 'heights',
      'florida', 'oklahoma', 'lake', 'rv', 'pipeline', 'xl', 'light',
    ],
  },
  'copper-mountain': {
    short: 'Copper',
    path: 'Copper-Mountain',
    area: 'Copper Mountain, Colorado',
    names: ['copper mountain'],
    keywords: [['copper ski map', 'phrase']],
    negatives: ['college', 'copper harbor', 'copper canyon', 'arizona', 'az', 'mine'],
  },
  'winter-park': {
    short: 'Winter Park',
    path: 'Winter-Park',
    area: 'Mary Jane and Winter Park',
    names: ['winter park resort', 'winter park colorado'],
    keywords: [
      ['winter park trail map', 'exact'],
      ['winter park ski map', 'exact'],
      ['winter park ski map', 'phrase'],
      ['winter park ski trails', 'phrase'],
      ['mary jane trail map', 'exact'],
    ],
    negatives: ['florida', 'fl', 'orlando', 'rollins', 'cady way', 'trestle', 'chamber'],
  },
  'park-city': {
    short: 'Park City',
    path: 'Park-City',
    area: 'Park City and Canyons',
    names: ['park city mountain', 'canyons village'],
    keywords: [
      ['park city trail map', 'exact'],
      ['park city ski map', 'exact'],
      ['park city ski map', 'phrase'],
      ['park city ski trails', 'phrase'],
      ['park city canyons trail map', 'phrase'],
    ],
    negatives: [
      'deer valley', 'kansas', 'kentucky', 'montana', 'illinois', 'round valley',
      'mountain trails', 'woodward', 'olympic park', 'main street',
    ],
  },
  'whistler-blackcomb': {
    short: 'Whistler',
    path: 'Whistler',
    area: 'Whistler and Blackcomb',
    names: ['whistler blackcomb', 'whistler', 'blackcomb'],
    keywords: [
      ['whistler piste map', 'phrase'],
      ['whistler blackcomb piste map', 'phrase'],
      ['whistler mountain map', 'phrase'],
    ],
    negatives: [
      'jasper', 'whistlers', 'olympic park', 'callaghan', 'lost lake', 'sliding',
      'garibaldi', 'sea to sky', 'village map', 'train',
    ],
  },
  'palisades-tahoe': {
    short: 'Palisades',
    path: 'Palisades-Tahoe',
    area: 'Palisades and Alpine Meadows',
    // Alpine is the old Alpine Meadows, which people still search for
    names: ['palisades tahoe', 'alpine meadows'],
    keywords: [
      ['palisades ski map', 'exact'],
      ['palisades ski map', 'phrase'],
      ['palisades ski trails', 'phrase'],
    ],
    negatives: ['interstate', 'pacific palisades', 'palisades park', 'new jersey', 'nj', 'campground', 'rainier', 'apartments'],
  },
  'big-sky': {
    short: 'Big Sky',
    path: 'Big-Sky',
    area: 'Lone Peak to Spanish Peaks',
    // Moonlight Basin, merged into Big Sky, is still what people call its north side
    names: ['big sky resort', 'big sky montana', 'moonlight basin'],
    keywords: [
      ['big sky trail map', 'exact'],
      ['big sky ski map', 'exact'],
      ['big sky ski map', 'phrase'],
      ['big sky ski trails', 'phrase'],
    ],
    // the conference's sports, the TV series, the brewery, the other Big Skies
    negatives: [
      'football', 'basketball', 'softball', 'volleyball', 'tournament', 'tv', 'series', 'episode', 'cast',
      'brewing', 'beer', 'australia', 'country',
    ],
  },
  heavenly: {
    short: 'Heavenly',
    path: 'Heavenly',
    area: 'California and Nevada Sides',
    // bare "heavenly" means too much else: only with "ski", "tahoe" or a map
    names: ['heavenly ski resort', 'heavenly lake tahoe', 'heavenly tahoe'],
    keywords: [
      ['heavenly trail map', 'exact'],
      ['heavenly ski map', 'exact'],
      ['heavenly ski map', 'phrase'],
      ['heavenly ski trails', 'phrase'],
    ],
    // the other heavenlies: food, beds, spas, faith, games and shows
    negatives: [
      'hash', 'ham', 'bed', 'bedding', 'mattress', 'spa', 'father', 'bodies', 'kingdom', 'creatures', 'delusion',
      'sword', 'hawaiian', 'cookie', 'recipe', 'dessert',
    ],
  },
  'deer-valley': {
    short: 'Deer Valley',
    path: 'Deer-Valley',
    area: 'Bald Mountain to East Village',
    names: ['deer valley resort', 'deer valley utah'],
    keywords: [
      ['deer valley trail map', 'exact'],
      ['deer valley ski map', 'exact'],
      ['deer valley ski map', 'phrase'],
      ['deer valley ski trails', 'phrase'],
      ['deer valley east village map', 'phrase'],
    ],
    // the other Deer Valleys (Arizona, California, Pennsylvania), and summer
    negatives: [
      'arizona', 'az', 'phoenix', 'california', 'antioch', 'pennsylvania', 'pa', 'hershey', 'unified', 'high school',
      'mountain bike', 'bike', 'hiking', 'concert', 'amphitheater', 'grocery',
    ],
  },
  steamboat: {
    short: 'Steamboat',
    path: 'Steamboat',
    area: 'Mt. Werner to Mahogany Ridge',
    // bare "steamboat" means boats: only with the resort's names or a map
    names: ['steamboat ski resort', 'steamboat springs', 'steamboat resort'],
    keywords: [
      ['steamboat trail map', 'exact'],
      ['steamboat ski map', 'exact'],
      ['steamboat ski map', 'phrase'],
      ['steamboat ski trails', 'phrase'],
    ],
    // the boats, the river and the town's other trails and springs
    negatives: ['boat', 'boats', 'paddle', 'river', 'cruise', 'willie', 'hot springs', 'strawberry', 'fish creek', 'rabbit ears pass'],
  },
  'mt-bachelor': {
    short: 'Mt. Bachelor',
    path: 'Mt-Bachelor',
    area: 'Summit, Westside & Eastside',
    names: ['mt bachelor', 'mount bachelor'],
    keywords: [],
    // the volcano (climbs, geology) and the TV show; summer and Nordic are the campaign's negatives
    negatives: ['climb', 'climbing', 'volcano', 'eruption', 'geology', 'the bachelor', 'bachelorette'],
  },
  mammoth: {
    short: 'Mammoth',
    path: 'Mammoth',
    area: 'Summit to the Back Side',
    // bare "mammoth" means the animal (and much else): only with the resort's names or a map
    names: ['mammoth mountain', 'mammoth lakes', 'mammoth ski resort'],
    keywords: [
      ['mammoth trail map', 'exact'],
      ['mammoth ski map', 'exact'],
      ['mammoth ski map', 'phrase'],
      ['mammoth ski trails', 'phrase'],
    ],
    // the animals, the caves and the other Mammoths (the storage brand, the cards, the town's summer)
    negatives: [
      'woolly', 'extinct', 'fossil', 'tusk', 'elephant', 'cave', 'kentucky', 'national park', 'storage', 'hunting',
      'mountain bike', 'bike park', 'fishing', 'hiking', 'campground', 'zip code',
    ],
  },
  snowmass: {
    short: 'Snowmass',
    path: 'Snowmass',
    area: 'Elk Camp to the Cirque',
    names: ['snowmass', 'aspen snowmass', 'snowmass village'],
    keywords: [],
    // the other mountain (the 14er), the village's summer, the conference center and the rodeo
    negatives: ['snowmass mountain 14er', 'snowmass lake', 'maroon bells', 'rodeo', 'balloon festival',
      'mountain bike', 'bike park', 'hiking', 'conference center', 'golf'],
  },
};

/** Keywords for a resort's names: the first gets the full set. */
function keywordsFor(names) {
  const [first, ...rest] = names;
  const kws = [
    [`${first} trail map`, 'exact'],
    [`${first} ski map`, 'exact'],
    [`${first} trail map`, 'phrase'],
    [`${first} ski map`, 'phrase'],
    [`${first} ski trails`, 'phrase'],
    [`${first} trail list`, 'phrase'],
    [`${first} run map`, 'phrase'],
  ];
  if (!first.includes(' ')) kws.push([`${first} mountain map`, 'phrase']);
  for (const n of rest) kws.push([`${n} trail map`, 'exact'], [`${n} trail map`, 'phrase'], [`${n} ski map`, 'phrase']);
  return kws;
}

// Searches the trail-map campaigns don't want (both campaigns): what else
// people look for with a resort's name. Negative keywords don't match plurals
// or misspellings, so those are listed too.
const TRAIL_MAP_NEGATIVES = [
  // summer and other sports: the app is winter trail maps
  'bike', 'bikes', 'biking', 'mtb', 'mountain bike', 'mountain biking', 'bike park', 'hike', 'hikes',
  'hiking', 'summer', 'golf', 'disc golf', 'zipline', 'zip line', 'alpine slide', 'coaster',
  'trail running', 'foliage', 'fishing', 'camping', 'horseback', 'atv', 'snowmobile', 'snowmobiling',
  'snowshoe', 'snowshoeing', 'nordic', 'cross country', 'xc', 'fat bike', 'tubing', 'ice skating',
  'waterpark', 'water park',
  // lodging, food, property
  'hotel', 'hotels', 'lodging', 'condo', 'condos', 'airbnb', 'vrbo', 'rental', 'rentals', 'real estate',
  'homes for sale', 'restaurant', 'restaurants', 'dining', 'menu', 'brewery',
  // tickets and prices
  'lift ticket', 'lift tickets', 'ticket', 'tickets', 'epic pass', 'ikon pass', 'season pass',
  'indy pass', 'price', 'prices', 'cost', 'deals', 'discount', 'coupon',
  // reports the app doesn't have
  'weather', 'forecast', 'snow report', 'webcam', 'webcams', 'web cam', 'cam', 'cams', 'live cam',
  'grooming report', 'lift status', 'trails open', 'open today', 'closed', 'closure', 'closures',
  'hours', 'opening day', 'closing day', 'snowfall', 'snow depth', 'parking', 'shuttle', 'bus',
  'directions', 'airport', 'address',
  // jobs
  'job', 'jobs', 'employment', 'careers', 'hiring', 'salary', 'internship',
  // trail-map merchandise
  'poster', 'posters', 'framed', 'canvas', 'art', 'artwork', 'decor', 'puzzle', 'jigsaw', 'shirt',
  't shirt', 'tshirt', 'hoodie', 'sweatshirt', 'mug', 'glass', 'glasses', 'pint glass', 'blanket',
  'pillow', 'rug', 'ornament', 'sticker', 'stickers', 'wallpaper', 'vintage', '3d', 'wood', 'wooden',
  'carved', 'painting', 'etsy', 'amazon', 'buy', 'shop',
  // news
  'accident', 'death', 'died', 'dies', 'killed', 'injury', 'lawsuit', 'avalanche', 'crash', 'news',
  // other services
  'wedding', 'weddings', 'conference', 'employee', 'lessons', 'ski school', 'demo', 'tuning',
  'lockers', 'daycare', 'childcare',
];

// ------------------------------------------------------- shared ad lines

const RESORT_SHARED_HEADLINES = [
  'Tap a Run to Mark It Skied',
  "See What's Left to Ski",
  'Free, No App to Download',
  'Works Offline on the Mountain',
  'Log Every Ski Trip',
  'Share Your Trip Recap',
  'Skier-Rated Trail Conditions',
  'My Ski Runs',
];

const FREE_LINE = 'A free, independent web app. No app download or sign-up, and it works offline once opened.';
const TRIPS_LINE = 'Log every trip, see runs that are new to you and your difficulty mix, and share a recap.';

// ------------------------------------------------- "Ski Run Tracker" ads
// pinned: the two headlines that alternate in position 1 (the search's own
// words); headlines: the group's own lines, then TRACKER_SHARED_HEADLINES fill
// it to 15; path: display path 1.

const TRACKER_GROUPS = [
  {
    name: 'Ski Run Tracker',
    path: 'Ski-Run-Tracker',
    pinned: ['Free Ski Run Tracker', 'Track Every Run You Ski'],
    headlines: ['East Coast to the West Coast'],
    lead: "Tap the runs you ski on the resort's own trail map. See your progress and what's left.",
    keywords: [
      ['ski run tracker', 'exact'],
      ['ski trail tracker', 'exact'],
      ['track ski runs', 'exact'],
      ['ski run tracker', 'phrase'],
      ['ski trail tracker', 'phrase'],
      ['ski run tracker app', 'phrase'],
      ['track ski runs', 'phrase'],
      ['track my ski runs', 'phrase'],
      ['app to track ski runs', 'phrase'],
      ['ski run log', 'phrase'],
      ['ski run logger', 'phrase'],
      ['ski run counter', 'phrase'],
      ['ski runs app', 'phrase'],
      ['snowboard run tracker', 'phrase'],
      ['ski tracker app', 'phrase'],
      ['ski tracking app', 'phrase'],
      ['free ski tracker', 'phrase'],
    ],
  },
  {
    name: 'Ski Trail Checklist',
    path: 'Trail-Checklist',
    pinned: ['Your Ski Trail Checklist', 'Check Off Every Ski Run'],
    headlines: ['Ski Every Trail on the Map', 'Progress by Difficulty'],
    lead: "Every run on the trail map is a checkbox. Tap the ones you ski and see what's left.",
    keywords: [
      ['ski trail checklist', 'exact'],
      ['ski every run', 'exact'],
      ['ski trail checklist', 'phrase'],
      ['ski run checklist', 'phrase'],
      ['ski every run', 'phrase'],
      ['ski every trail', 'phrase'],
      ['ski resort checklist', 'phrase'],
      ['ski bucket list app', 'phrase'],
      ['ski run list app', 'phrase'],
      ['runs skied', 'phrase'],
      ['trails skied', 'phrase'],
    ],
  },
  {
    name: 'Ski Trip Log',
    path: 'Ski-Trip-Log',
    pinned: ['Your Ski Trip Log', 'Log Every Ski Day'],
    headlines: ['Day-by-Day Run Log', 'Runs That Are New to You', 'Free Ski Journal App'],
    lead: 'Name each trip, tap the runs you ski, and get a day-by-day log with your toughest runs.',
    keywords: [
      ['ski log app', 'exact'],
      ['ski journal app', 'exact'],
      ['ski log app', 'phrase'],
      ['ski journal app', 'phrase'],
      ['ski diary app', 'phrase'],
      ['ski day log', 'phrase'],
      ['ski trip log', 'phrase'],
      ['ski days tracker', 'phrase'],
      ['ski logbook', 'phrase'],
      ['snowboard log app', 'phrase'],
      ['ski journal', 'phrase'],
      ['ski log', 'phrase'],
    ],
  },
  {
    name: 'Interactive Trail Maps',
    path: 'Trail-Maps',
    pinned: ['Interactive Ski Trail Maps', 'Offline Ski Trail Maps'],
    headlines: ['Search Any Run by Name', 'Add It to Your Home Screen'],
    lead: "The resorts' own trail maps, every run clickable. Search a run and the map zooms to it.",
    keywords: [
      ['interactive ski trail map', 'exact'],
      ['ski trail maps', 'exact'],
      ['interactive ski trail map', 'phrase'],
      ['interactive ski map', 'phrase'],
      ['ski trail map app', 'phrase'],
      ['ski trail maps app', 'phrase'],
      ['ski resort map app', 'phrase'],
      ['ski map app', 'phrase'],
      ['offline ski map', 'phrase'],
      ['offline ski trail map', 'phrase'],
      ['ski resort trail maps', 'phrase'],
    ],
  },
  {
    name: 'Brand',
    path: 'Ski-Run-Tracker',
    pinned: ['My Ski Runs', 'My Ski Runs: Track Every Run'],
    headlines: [],
    lead: "Tap the runs you ski on the resort's own trail map. See your progress and what's left.",
    keywords: [
      ['myskiruns', 'exact'],
      ['my ski runs', 'exact'],
      ['myskiruns app', 'exact'],
      ['my ski runs', 'phrase'],
      ['my ski runs app', 'phrase'],
    ],
  },
];

// Tracking searches the app doesn't answer: automatic GPS tracking and
// watches, other apps by name, other "ski" things.
const TRACKER_NEGATIVES = [
  'gps', 'watch', 'apple watch', 'garmin', 'fitbit', 'smartwatch', 'wear os', 'speed', 'speedometer',
  'altimeter', 'vertical', 'heart rate', 'strava', 'slopes app', 'ski tracks', 'skitracks', 'epicmix',
  'epic mix', 'epic', 'my epic', 'ikon', 'fatmap', 'snocru', 'skiing yeti', 'trace snow', 'carv',
  'jet ski', 'jetski', 'water ski', 'waterski', 'ski boat', 'skierg', 'ski erg', 'ski machine',
  'simulator', 'indoor', 'game', 'games', 'roblox', 'minecraft', 'nordic', 'cross country', 'xc',
  'backcountry', 'touring', 'skate ski', 'apk', 'mod', 'hack', 'job', 'jobs', 'career', 'careers',
  'beacon', 'transceiver', 'avalanche', 'airtag', 'device', 'lift line', 'wait time', 'wait times',
  'weather', 'forecast', 'snow report', 'cabin', 'cabins', 'log home', 'log homes', 'magazine',
  'subscription',
];

// ----------------------------------------------------------- assets

const CALLOUTS = (total, resorts) => [
  'Free to Use',
  'No App to Download',
  'No Sign-Up Needed',
  'Works Offline',
  'No GPS Needed',
  'Trip Recaps to Share',
  'Skier-Rated Conditions',
  `${total} Runs on ${resorts} Maps`,
  'Phone, Tablet or Computer',
  'Add to Your Home Screen',
];

// sitelinks of the "Ski Run Tracker" campaign: the best-known resorts
const TRACKER_SITELINKS = ['killington', 'stowe', 'vail', 'breckenridge', 'park-city', 'whistler-blackcomb'];

// Other map panels get sitelinks of their own (distinct pages); peak: the
// trail-list group whose runs the panel shows, for the run count
const PANEL_SITELINKS = {
  vail: [
    { panel: 'back-bowls', peak: 'back-bowls', text: 'Vail Back Bowls Map', line: 'Sun Down, Sun Up, China, Siberia' },
    { panel: 'blue-sky', peak: 'blue-sky', text: 'Blue Sky Basin Map', line: "Pete's Bowl and Earl's Bowl" },
  ],
  'palisades-tahoe': [
    { panel: 'alpine-front', peak: 'alpine', text: 'Alpine Meadows Trail Map', line: "Alpine's front and back sides" },
  ],
};

// ---------------------------------------------------------- checking

const LIMITS = { headline: 30, description: 90, path: 15, sitelink: 25, sitelinkLine: 35, callout: 25, snippet: 25 };
const errors = [];

/** The first alternative within the limit for `kind` (an error if none is). */
function fit(kind, ...alternatives) {
  const ok = alternatives.find((t) => t.length <= LIMITS[kind]);
  if (ok === undefined) errors.push(`${kind} over ${LIMITS[kind]} characters: "${alternatives.at(-1)}"`);
  return ok ?? alternatives.at(-1);
}

function checkText(kind, text, where) {
  if (text.length > LIMITS[kind]) errors.push(`${where}: ${kind} over ${LIMITS[kind]} characters: "${text}"`);
  if (!/^[\x20-\x7e]+$/.test(text)) errors.push(`${where}: non-ASCII character in "${text}"`);
  if (text !== text.trim() || text.includes('  ')) errors.push(`${where}: stray spaces in "${text}"`);
  if (kind === 'headline' && text.includes('!')) errors.push(`${where}: headlines can't have "!": "${text}"`);
  if (kind === 'path' && /\s/.test(text)) errors.push(`${where}: display path with a space: "${text}"`);
}

function checkKeyword(text, where) {
  if (!/^[a-z0-9][a-z0-9 '&.-]*$/.test(text)) errors.push(`${where}: keyword "${text}" has an unusual character`);
  if (text.length > 80 || text.split(' ').length > 10) errors.push(`${where}: keyword "${text}" too long`);
}

// ------------------------------------------------------------ build

const resorts = [];
for (const entry of RESORTS) {
  const ads = RESORT_ADS[entry.id];
  if (!ads) {
    errors.push(`resort "${entry.id}" (${entry.name}) has no entry in RESORT_ADS`);
    continue;
  }
  const { trails, peaks } = await import(`../../src/data/resorts/${entry.id}/trails.ts`);
  const perPeak = Object.fromEntries(peaks.map((p) => [p.id, trails.filter((t) => t.peak === p.id).length]));
  resorts.push({ ...entry, ...ads, count: trails.length, perPeak, campaign: EAST.has(entry.region) ? 'east' : 'west' });
}
for (const id of Object.keys(RESORT_ADS)) {
  if (!RESORTS.some((r) => r.id === id)) errors.push(`RESORT_ADS has "${id}", which isn't in src/resorts.ts`);
}

const total = resorts.reduce((n, r) => n + r.count, 0);
const resortUrl = (id, panel) => `${SITE}?resort=${id}${panel ? `&panel=${panel}` : ''}`;
const campaignName = Object.fromEntries(CAMPAIGNS.map((c) => [c.key, c.name]));

// "18 resorts in Vermont, ...": regions east to west (too many to list: the two ends)
const rank = (region) => (REGION_ORDER.includes(region) ? REGION_ORDER.indexOf(region) : REGION_ORDER.length);
const regions = [...new Set(resorts.map((r) => r.region))].sort((a, b) => rank(a) - rank(b));
const listed = (names) => `${names.slice(0, -1).join(', ')} and ${names.at(-1)}`;
const resortsLine = fit(
  'description',
  `${resorts.length} resorts in ${listed(regions)}.`,
  `${resorts.length} resorts in ${listed(regions.map((r) => (r === 'British Columbia' ? 'BC' : r)))}.`,
  `${resorts.length} resorts from ${regions[0]} to ${regions.at(-1)}.`,
);

const TRACKER_SHARED_HEADLINES = [
  'Tap the Runs You Skied',
  "On the Resort's Own Trail Map",
  'No GPS, Just Tap the Map',
  'Works Offline on the Mountain',
  fit('headline', `${resorts.length} Resorts, ${total.toLocaleString('en-US')} Runs`),
  "See What's Left to Ski",
  'Free, No App to Download',
  'Log Every Ski Trip',
  'Share Your Trip Recap',
  'Skier-Rated Trail Conditions',
  'Vail, Stowe, Park City & More',
  'My Ski Runs',
];

/** One ad group: its responsive search ad, keywords and negatives. */
const groups = [];

for (const r of resorts) {
  const name = r.name;
  const headlines = [
    { text: fit('headline', `${name} Trail Map`), pin: 1 },
    {
      text: fit('headline', `Interactive ${name} Trail Map`, `Interactive ${r.short} Trail Map`, `Interactive ${r.short} Map`),
      pin: 1,
    },
    { text: fit('headline', `${name} Run Tracker`, `${r.short} Run Tracker`) },
    {
      text: fit(
        'headline',
        `${r.count} ${r.short} Runs to Check Off`,
        `${r.count} ${r.short} Runs, One Map`,
        `${r.count} Runs to Check Off`,
      ),
    },
    { text: fit('headline', `Ski Every Run at ${r.short}`, `Ski Every ${r.short} Run`) },
    { text: fit('headline', `Track the ${r.short} Runs You Ski`, `Track Your ${r.short} Runs`) },
    { text: r.area },
    ...RESORT_SHARED_HEADLINES.map((text) => ({ text })),
  ];
  const descriptions = [
    fit(
      'description',
      `Tap any of the ${r.count} runs on the ${name} trail map to mark it skied. See what's left.`,
      `Tap any of ${r.count} runs on the ${name} trail map to mark it skied. See what's left.`,
      `Tap any of ${r.count} runs on the ${name} trail map to mark it skied.`,
    ),
    FREE_LINE,
    TRIPS_LINE,
    fit('description', `Rate today's conditions on any ${r.short} run and see what other skiers report.`),
  ];
  groups.push({
    campaign: r.campaign,
    name,
    url: resortUrl(r.id),
    path1: r.path,
    path2: 'Trail-Map',
    headlines,
    descriptions,
    keywords: [...keywordsFor(r.names), ...(r.keywords ?? [])],
    negatives: r.negatives ?? [],
  });
}

for (const g of TRACKER_GROUPS) {
  const headlines = g.pinned.map((text) => ({ text, pin: 1 }));
  for (const text of [...g.headlines, ...TRACKER_SHARED_HEADLINES]) {
    if (headlines.length < 15 && !headlines.some((h) => h.text === text)) headlines.push({ text });
  }
  groups.push({
    campaign: 'tracker',
    name: g.name,
    url: SITE,
    path1: g.path,
    path2: '',
    headlines,
    descriptions: [g.lead, FREE_LINE, TRIPS_LINE, resortsLine],
    keywords: g.keywords,
    negatives: [],
  });
}

const campaignNegatives = {
  east: TRAIL_MAP_NEGATIVES,
  west: TRAIL_MAP_NEGATIVES,
  tracker: TRACKER_NEGATIVES,
};

const sitelinkFor = (r) => ({
  text: fit('sitelink', `${r.name} Trail Map`, `${r.name} Map`, `${r.short} Trail Map`),
  line1: `${r.count} runs to check off`,
  line2: r.area,
  url: resortUrl(r.id),
});
// a campaign's resorts, the most runs first (snippets show 10 at most)
const inCampaign = (key) => resorts.filter((r) => r.campaign === key).sort((a, b) => b.count - a.count);
const sitelinks = {
  east: inCampaign('east').map(sitelinkFor),
  west: inCampaign('west').flatMap((r) => [
    sitelinkFor(r),
    ...(PANEL_SITELINKS[r.id] ?? []).map((p) => ({
      text: p.text,
      line1: `${r.perPeak[p.peak] ?? errors.push(`${r.id}: no trail-list group "${p.peak}"`)} runs to check off`,
      line2: p.line,
      url: resortUrl(r.id, p.panel),
    })),
  ]),
  tracker: TRACKER_SITELINKS.map((id) => sitelinkFor(resorts.find((r) => r.id === id))),
};

const callouts = CALLOUTS(total.toLocaleString('en-US'), resorts.length);

// Structured snippets: Google shows at most 10 values
const snippets = {
  east: inCampaign('east').map((r) => r.name).slice(0, 10),
  west: inCampaign('west').map((r) => r.name).slice(0, 10),
  tracker: regions.slice(0, 10),
};

// ------------------------------------------------------------ checks

for (const g of groups) {
  const where = `${campaignName[g.campaign]} > ${g.name}`;
  if (g.headlines.length < 3 || g.headlines.length > 15) errors.push(`${where}: ${g.headlines.length} headlines`);
  if (g.descriptions.length < 2 || g.descriptions.length > 4) errors.push(`${where}: ${g.descriptions.length} descriptions`);
  const seen = new Set();
  for (const h of g.headlines) {
    checkText('headline', h.text, where);
    if (seen.has(h.text.toLowerCase())) errors.push(`${where}: headline twice: "${h.text}"`);
    seen.add(h.text.toLowerCase());
  }
  for (const d of g.descriptions) checkText('description', d, where);
  for (const p of [g.path1, g.path2].filter(Boolean)) checkText('path', p, where);
  const kwSeen = new Set();
  for (const [text, match] of g.keywords) {
    checkKeyword(text, where);
    if (kwSeen.has(`${match}:${text}`)) errors.push(`${where}: keyword twice: ${match} "${text}"`);
    kwSeen.add(`${match}:${text}`);
  }
  for (const n of g.negatives) checkKeyword(n, `${where} (negative)`);
}
for (const [key, list] of Object.entries(campaignNegatives)) {
  if (new Set(list).size !== list.length) errors.push(`${campaignName[key]}: a negative keyword is listed twice`);
  for (const n of list) checkKeyword(n, `${campaignName[key]} (negative)`);
}
// a keyword containing one of its negatives would never show an ad
const contains = (text, phrase) => ` ${text} `.includes(` ${phrase} `);
for (const g of groups) {
  for (const n of [...campaignNegatives[g.campaign], ...g.negatives]) {
    for (const [text] of g.keywords) {
      if (contains(text, n)) errors.push(`${campaignName[g.campaign]} > ${g.name}: negative "${n}" blocks keyword "${text}"`);
    }
  }
}
for (const [key, list] of Object.entries(sitelinks)) {
  const where = `${campaignName[key]} sitelinks`;
  for (const s of list) {
    checkText('sitelink', s.text, where);
    checkText('sitelinkLine', s.line1, where);
    checkText('sitelinkLine', s.line2, where);
  }
  if (new Set(list.map((s) => s.url)).size !== list.length) errors.push(`${where}: two sitelinks share a page`);
  if (new Set(list.map((s) => s.text)).size !== list.length) errors.push(`${where}: two sitelinks share a text`);
}
for (const c of callouts) checkText('callout', c, 'callouts');
for (const [key, values] of Object.entries(snippets)) {
  if (values.length < 3) errors.push(`${campaignName[key]}: a structured snippet needs 3 values`);
  for (const v of values) checkText('snippet', v, `${campaignName[key]} snippet`);
}

if (errors.length) {
  console.error(`Not written: ${errors.length} problem(s)\n  ${errors.join('\n  ')}`);
  process.exit(1);
}

// ------------------------------------------------------------ write

/** CSV text: a header row, then one row per object. */
function csv(columns, rows) {
  const cell = (v) => {
    const s = v == null ? '' : String(v);
    return /[",\n]/.test(s) ? `"${s.replaceAll('"', '""')}"` : s;
  };
  return [columns, ...rows.map((r) => columns.map((c) => r[c]))].map((r) => r.map(cell).join(',')).join('\n') + '\n';
}

const MATCH = { exact: 'Exact', phrase: 'Phrase' };
const files = {
  '1-campaigns.csv': csv(
    ['Campaign', 'Campaign type', 'Campaign status', 'Budget', 'Networks', 'Bid strategy type', 'Maximum CPC bid limit',
      'Languages', 'Final URL suffix'],
    CAMPAIGNS.map((c) => ({
      Campaign: c.name,
      'Campaign type': 'Search',
      'Campaign status': 'Paused',
      Budget: c.budget.toFixed(2),
      Networks: 'Google Search',
      'Bid strategy type': 'Maximize clicks',
      'Maximum CPC bid limit': c.cpcLimit.toFixed(2),
      Languages: c.languages,
      'Final URL suffix': `utm_source=google&utm_medium=cpc&utm_campaign=${c.name.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`,
    })),
  ),
  '2-locations.csv': csv(
    ['Campaign', 'Location', 'Location ID'],
    CAMPAIGNS.flatMap((c) => LOCATIONS.map((l) => ({ Campaign: c.name, Location: l.name, 'Location ID': l.id }))),
  ),
  '3-ad-groups.csv': csv(
    ['Campaign', 'Ad group', 'Ad group status'],
    groups.map((g) => ({ Campaign: campaignName[g.campaign], 'Ad group': g.name, 'Ad group status': 'Enabled' })),
  ),
  '4-keywords.csv': csv(
    ['Campaign', 'Ad group', 'Keyword', 'Criterion type', 'Status'],
    groups.flatMap((g) =>
      g.keywords.map(([text, match]) => ({
        Campaign: campaignName[g.campaign],
        'Ad group': g.name,
        Keyword: text,
        'Criterion type': MATCH[match],
        Status: 'Enabled',
      })),
    ),
  ),
  '5-negative-keywords.csv': csv(
    ['Campaign', 'Ad group', 'Keyword', 'Criterion type'],
    [
      ...CAMPAIGNS.flatMap((c) =>
        campaignNegatives[c.key].map((k) => ({ Campaign: c.name, Keyword: k, 'Criterion type': 'Campaign negative phrase' })),
      ),
      ...groups.flatMap((g) =>
        g.negatives.map((k) => ({
          Campaign: campaignName[g.campaign],
          'Ad group': g.name,
          Keyword: k,
          'Criterion type': 'Negative phrase',
        })),
      ),
    ],
  ),
  '6-responsive-search-ads.csv': csv(
    [
      'Campaign', 'Ad group', 'Status', 'Final URL', 'Path 1', 'Path 2',
      ...Array.from({ length: 15 }, (_, i) => [`Headline ${i + 1}`, `Headline ${i + 1} position`]).flat(),
      ...Array.from({ length: 4 }, (_, i) => [`Description ${i + 1}`, `Description ${i + 1} position`]).flat(),
    ],
    groups.map((g) => ({
      Campaign: campaignName[g.campaign],
      'Ad group': g.name,
      Status: 'Enabled',
      'Final URL': g.url,
      'Path 1': g.path1,
      'Path 2': g.path2,
      ...Object.fromEntries(g.headlines.flatMap((h, i) => [[`Headline ${i + 1}`, h.text], [`Headline ${i + 1} position`, h.pin ?? '']])),
      ...Object.fromEntries(g.descriptions.map((d, i) => [`Description ${i + 1}`, d])),
    })),
  ),
  '7-sitelinks.csv': csv(
    ['Campaign', 'Link text', 'Description line 1', 'Description line 2', 'Final URL'],
    CAMPAIGNS.flatMap((c) =>
      sitelinks[c.key].map((s) => ({
        Campaign: c.name,
        'Link text': s.text,
        'Description line 1': s.line1,
        'Description line 2': s.line2,
        'Final URL': s.url,
      })),
    ),
  ),
  '8-callouts.csv': csv(
    ['Campaign', 'Callout text'],
    CAMPAIGNS.flatMap((c) => callouts.map((t) => ({ Campaign: c.name, 'Callout text': t }))),
  ),
  '9-structured-snippets.csv': csv(
    ['Campaign', 'Header', 'Snippet values'],
    CAMPAIGNS.map((c) => ({ Campaign: c.name, Header: 'Destinations', 'Snippet values': snippets[c.key].join(';') })),
  ),
};

mkdirSync(OUT, { recursive: true });
for (const [name, text] of Object.entries(files)) writeFileSync(join(OUT, name), text);

// preview.md: every ad, keyword and asset, for reading and review
const md = [
  '# Google Ads campaign: preview',
  '',
  `Generated by \`npm run ads:build\` from \`build.mjs\` (don't edit by hand). ${resorts.length} resorts, ` +
    `${total.toLocaleString('en-US')} runs. Headlines marked *(pin 1)* alternate in position 1; Google picks the ` +
    'rest of each ad from the lists.',
  '',
];
for (const c of CAMPAIGNS) {
  md.push(`## ${c.name}`, '');
  md.push(
    `$${c.budget.toFixed(2)}/day, Maximize clicks (max CPC $${c.cpcLimit.toFixed(2)}), Google Search only, ` +
      `${LOCATIONS.map((l) => l.name).join(' and ')}, languages ${c.languages}.`,
    '',
  );
  for (const g of groups.filter((x) => x.campaign === c.key)) {
    const display = `myskiruns.app/${[g.path1, g.path2].filter(Boolean).join('/')}`;
    md.push(`### ${g.name}`, '', `Final URL: ${g.url} (shown as ${display})`, '');
    md.push('| Headlines | | Descriptions |', '|---|---|---|');
    for (let i = 0; i < Math.max(g.headlines.length, g.descriptions.length); i++) {
      const h = g.headlines[i];
      md.push(`| ${h ? `${h.text}${h.pin ? ' *(pin 1)*' : ''}` : ''} | ${h ? h.text.length : ''} | ${g.descriptions[i] ?? ''} |`);
    }
    const kws = g.keywords.map(([t, m]) => (m === 'exact' ? `[${t}]` : `"${t}"`));
    md.push('', `Keywords: ${kws.join(', ')}`);
    if (g.negatives.length) md.push('', `Negative keywords (this ad group): ${g.negatives.join(', ')}`);
    md.push('');
  }
  md.push(`**Negative keywords (whole campaign, phrase match):** ${campaignNegatives[c.key].join(', ')}`, '');
  md.push('**Sitelinks:**', '', '| Text | Line 1 | Line 2 | Page |', '|---|---|---|---|');
  for (const s of sitelinks[c.key]) md.push(`| ${s.text} | ${s.line1} | ${s.line2} | ${s.url} |`);
  md.push('', `**Callouts:** ${callouts.join(' · ')}`, '', `**Structured snippet (Destinations):** ${snippets[c.key].join(', ')}`, '');
}
writeFileSync(join(HERE, 'preview.md'), md.join('\n'));

const count = (k) => groups.reduce((n, g) => n + g[k].length, 0);
console.log(
  `Wrote ${Object.keys(files).length} files to ${OUT} and preview.md: ${CAMPAIGNS.length} campaigns, ` +
    `${groups.length} ad groups, ${count('keywords')} keywords, ` +
    `${Object.values(campaignNegatives).reduce((n, l) => n + l.length, 0) + count('negatives')} negative keywords, ` +
    `${groups.length} ads, ${Object.values(sitelinks).reduce((n, l) => n + l.length, 0)} sitelinks.`,
);
