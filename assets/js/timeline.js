const rows = [
  [
    '2007',
    'iPhone (1st generation)',
    '2007-06-29',
    '$499 / $599',
    'iPhone OS 1',
    '3.5 in',
    'Aluminium rear with black plastic antenna cap; multitouch glass display.',
    'Apple combined phone, widescreen iPod and internet communicator in one pocket device.',
  ],
  [
    '2008',
    'iPhone 3G',
    '2008-07-11',
    '$199 / $299*',
    'iPhone OS 2',
    '3.5 in',
    'Curved plastic back; GPS and 3G cellular data.',
    'App Store arrived with iPhone OS 2, turning the phone into a software platform.',
  ],
  [
    '2009',
    'iPhone 3GS',
    '2009-06-19',
    '$199 / $299*',
    'iPhone OS 3',
    '3.5 in',
    'Glossy plastic shell; faster internals and video recording.',
    'The “S” generation focused on speed, voice control and a much stronger camera.',
  ],
  [
    '2010',
    'iPhone 4',
    '2010-06-24',
    '$199 / $299*',
    'iOS 4',
    '3.5 in',
    'Flat glass front and back framed by stainless steel.',
    'Retina display, FaceTime, HD video and the first front-facing iPhone camera.',
  ],
  [
    '2011',
    'iPhone 4s',
    '2011-10-14',
    '$199 / $299*',
    'iOS 5',
    '3.5 in',
    'Retained the glass-and-steel silhouette; improved antenna design.',
    'Siri debuted alongside iCloud, iMessage and an 8MP camera.',
  ],
  [
    '2012',
    'iPhone 5',
    '2012-09-21',
    '$199 / $299 / $399*',
    'iOS 6',
    '4 in',
    'Two-tone anodised aluminium body; Lightning connector.',
    'A taller Retina display and LTE arrived in a notably thinner, lighter enclosure.',
  ],
  [
    '2013',
    'iPhone 5c',
    '2013-09-20',
    '$99 / $199*',
    'iOS 7',
    '4 in',
    'Polycarbonate shell in vivid colours over a reinforced steel frame.',
    'A more colourful, lower-cost companion to the 5s, with the same screen size.',
  ],
  [
    '2013',
    'iPhone 5s',
    '2013-09-20',
    '$199 / $299 / $399*',
    'iOS 7',
    '4 in',
    'Aluminium body in silver, gold or space gray; home-button sensor.',
    'Touch ID and the first 64-bit smartphone processor arrived together.',
  ],
  [
    '2014',
    'iPhone 6',
    '2014-09-19',
    '$199 / $299 / $399*',
    'iOS 8',
    '4.7 in',
    'Rounded aluminium enclosure; protruding camera ring.',
    'A larger display, Apple Pay and a new thin profile marked a major scale shift.',
  ],
  [
    '2014',
    'iPhone 6 Plus',
    '2014-09-19',
    '$299 / $399 / $499*',
    'iOS 8',
    '5.5 in',
    'Larger rounded aluminium body with optical image stabilisation.',
    'The first Plus model brought iPhone into the large-screen category.',
  ],
  [
    '2015',
    'iPhone 6s',
    '2015-09-25',
    '$199 / $299 / $399*',
    'iOS 9',
    '4.7 in',
    'Aluminium body strengthened with 7000-series alloy; 3D Touch.',
    'Live Photos, 4K video and pressure-sensitive display interactions.',
  ],
  [
    '2015',
    'iPhone 6s Plus',
    '2015-09-25',
    '$299 / $399 / $499*',
    'iOS 9',
    '5.5 in',
    'Large aluminium body with optical image stabilisation.',
    'The Plus size paired 3D Touch with a stabilised camera and 4K capture.',
  ],
  [
    '2016',
    'iPhone SE (1st generation)',
    '2016-03-31',
    '$399 / $499',
    'iOS 9.3',
    '4 in',
    'Compact aluminium-and-glass form based on the iPhone 5s.',
    'A small-screen model with contemporary A9 performance and a 12MP camera.',
  ],
  [
    '2016',
    'iPhone 7',
    '2016-09-16',
    '$649',
    'iOS 10',
    '4.7 in',
    'Water-resistant body; solid-state home button; no headphone jack.',
    'Stereo speakers, optical stabilisation and a brighter wide-colour display.',
  ],
  [
    '2016',
    'iPhone 7 Plus',
    '2016-09-16',
    '$769',
    'iOS 10',
    '5.5 in',
    'Dual camera array introduced on the larger model.',
    'Dual 12MP cameras introduced optical zoom and Portrait mode.',
  ],
  [
    '2017',
    'iPhone 8',
    '2017-09-22',
    '$699 / $849',
    'iOS 11',
    '4.7 in',
    'Glass back with aluminium frame; wireless charging.',
    'A familiar home-button design gained A11 Bionic and True Tone display.',
  ],
  [
    '2017',
    'iPhone 8 Plus',
    '2017-09-22',
    '$799 / $949',
    'iOS 11',
    '5.5 in',
    'Glass back with dual camera and aluminium frame.',
    'Wireless charging and improved Portrait Lighting came to the Plus form.',
  ],
  [
    '2017',
    'iPhone X',
    '2017-11-03',
    '$999 / $1,149 / $1,349',
    'iOS 11',
    '5.8 in',
    'All-screen OLED face, stainless-steel frame and a camera notch.',
    'Face ID replaced Touch ID; gesture navigation and OLED defined a new era.',
  ],
  [
    '2018',
    'iPhone XS',
    '2018-09-21',
    '$999 / $1,149 / $1,349',
    'iOS 12',
    '5.8 in',
    'Stainless-steel frame, glass back and gold finish option.',
    'A12 Bionic, Smart HDR and improved water resistance refined the X design.',
  ],
  [
    '2018',
    'iPhone XS Max',
    '2018-09-21',
    '$1,099 / $1,249 / $1,449',
    'iOS 12',
    '6.5 in',
    'Largest iPhone display at launch; dual camera, stainless steel.',
    'The first Max model brought the X design to a 6.5-inch OLED screen.',
  ],
  [
    '2018',
    'iPhone XR',
    '2018-10-26',
    '$749 / $799 / $899',
    'iOS 12',
    '6.1 in',
    'Colourful aluminium frame and Liquid Retina LCD.',
    'Face ID and A12 performance reached a broad audience in six colours.',
  ],
  [
    '2019',
    'iPhone 11',
    '2019-09-20',
    '$699 / $749 / $849',
    'iOS 13',
    '6.1 in',
    'Dual-camera square; colour-infused glass back.',
    'Night mode and an ultrawide camera brought major photography gains.',
  ],
  [
    '2019',
    'iPhone 11 Pro',
    '2019-09-20',
    '$999 / $1,149 / $1,349',
    'iOS 13',
    '5.8 in',
    'Matte textured glass back; triple-camera system.',
    'The first “Pro” iPhone added an ultrawide lens and Super Retina XDR OLED.',
  ],
  [
    '2019',
    'iPhone 11 Pro Max',
    '2019-09-20',
    '$1,099 / $1,249 / $1,449',
    'iOS 13',
    '6.5 in',
    'Large matte glass body with triple-camera array.',
    'Pro camera features and longer battery life in the biggest 2019 model.',
  ],
  [
    '2020',
    'iPhone SE (2nd generation)',
    '2020-04-24',
    '$399 / $449',
    'iOS 13.4',
    '4.7 in',
    'Glass-and-aluminium body, home button and single rear camera.',
    'A13 Bionic brought flagship-era performance to a familiar compact design.',
  ],
  [
    '2020',
    'iPhone 12 mini',
    '2020-11-13',
    '$699 / $749 / $849',
    'iOS 14',
    '5.4 in',
    'Flat-edge aluminium frame; smallest 5G iPhone of the era.',
    'OLED, Ceramic Shield and 5G came in a genuinely compact form.',
  ],
  [
    '2020',
    'iPhone 12',
    '2020-10-23',
    '$799 / $849 / $949',
    'iOS 14',
    '6.1 in',
    'Flat-edge aluminium design with Ceramic Shield front.',
    '5G, OLED across the lineup and MagSafe accessories.',
  ],
  [
    '2020',
    'iPhone 12 Pro',
    '2020-10-23',
    '$999 / $1,099 / $1,299',
    'iOS 14',
    '6.1 in',
    'Stainless-steel frame, LiDAR scanner and triple cameras.',
    'Dolby Vision HDR video and LiDAR expanded creative and AR uses.',
  ],
  [
    '2020',
    'iPhone 12 Pro Max',
    '2020-11-13',
    '$1,099 / $1,199 / $1,399',
    'iOS 14',
    '6.7 in',
    'Largest display; sensor-shift stabilisation on main camera.',
    'A larger sensor and longer telephoto made this the camera flagship.',
  ],
  [
    '2021',
    'iPhone 13 mini',
    '2021-09-24',
    '$699 / $799',
    'iOS 15',
    '5.4 in',
    'Smaller notch, diagonal dual cameras and flat edges.',
    'Cinematic mode and improved battery life extended the mini line.',
  ],
  [
    '2021',
    'iPhone 13',
    '2021-09-24',
    '$799 / $899',
    'iOS 15',
    '6.1 in',
    'Diagonal dual-camera layout; smaller Face ID notch.',
    'Sensor-shift stabilisation and Cinematic video arrived on the standard model.',
  ],
  [
    '2021',
    'iPhone 13 Pro',
    '2021-09-24',
    '$999 / $1,099 / $1,299',
    'iOS 15',
    '6.1 in',
    'ProMotion display and triple camera array.',
    '120Hz ProMotion and macro photography came to iPhone Pro.',
  ],
  [
    '2021',
    'iPhone 13 Pro Max',
    '2021-09-24',
    '$1,099 / $1,199 / $1,399',
    'iOS 15',
    '6.7 in',
    'Large stainless-steel body with ProMotion and triple cameras.',
    'Longer battery life, ProMotion and a 3x telephoto lens.',
  ],
  [
    '2022',
    'iPhone SE (3rd generation)',
    '2022-03-18',
    '$429 / $479 / $579',
    'iOS 15.4',
    '4.7 in',
    'Classic home-button form with glass back and aluminium frame.',
    '5G and A15 Bionic kept the compact Touch ID design current.',
  ],
  [
    '2022',
    'iPhone 14',
    '2022-09-16',
    '$799 / $899 / $1,099',
    'iOS 16',
    '6.1 in',
    'Flat-edge aluminium design; dual cameras.',
    'Crash Detection and Emergency SOS via satellite introduced new safety tools.',
  ],
  [
    '2022',
    'iPhone 14 Plus',
    '2022-10-07',
    '$899 / $999 / $1,199',
    'iOS 16',
    '6.7 in',
    'Large display in a lighter, dual-camera standard design.',
    'The Plus name returned, bringing a large screen without Pro camera hardware.',
  ],
  [
    '2022',
    'iPhone 14 Pro',
    '2022-09-16',
    '$999 / $1,099 / $1,299',
    'iOS 16',
    '6.1 in',
    'Always-On display with Dynamic Island; 48MP main camera.',
    'Dynamic Island transformed the front sensor area into a live interface.',
  ],
  [
    '2022',
    'iPhone 14 Pro Max',
    '2022-09-16',
    '$1,099 / $1,199 / $1,399',
    'iOS 16',
    '6.7 in',
    'Large Always-On OLED; Dynamic Island and triple cameras.',
    '48MP imaging and always-on display marked the next Pro camera era.',
  ],
  [
    '2023',
    'iPhone 15',
    '2023-09-22',
    '$799 / $899 / $1,099',
    'iOS 17',
    '6.1 in',
    'Colour-infused glass back, contoured edges and USB-C port.',
    'USB-C replaced Lightning; Dynamic Island reached the standard line.',
  ],
  [
    '2023',
    'iPhone 15 Plus',
    '2023-09-22',
    '$899 / $999 / $1,199',
    'iOS 17',
    '6.7 in',
    'Large glass-and-aluminium design; 48MP dual camera.',
    'USB-C and a 48MP main camera in a large-screen non-Pro model.',
  ],
  [
    '2023',
    'iPhone 15 Pro',
    '2023-09-22',
    '$999 / $1,099 / $1,299',
    'iOS 17',
    '6.1 in',
    'Grade 5 titanium, contoured edges and Action button.',
    'A17 Pro enabled console-class gaming; USB-C supports fast data.',
  ],
  [
    '2023',
    'iPhone 15 Pro Max',
    '2023-09-22',
    '$1,199 / $1,399 / $1,599',
    'iOS 17',
    '6.7 in',
    'Titanium enclosure and tetraprism 5x telephoto camera.',
    'The first 5x optical zoom in an iPhone Pro Max, with USB-C.',
  ],
  [
    '2024',
    'iPhone 16',
    '2024-09-20',
    '$799 / $899 / $1,099',
    'iOS 18',
    '6.1 in',
    'Vertical dual-camera layout; Action button and Camera Control.',
    'Built for Apple Intelligence, with a dedicated camera control.',
  ],
  [
    '2024',
    'iPhone 16 Plus',
    '2024-09-20',
    '$899 / $999 / $1,199',
    'iOS 18',
    '6.7 in',
    'Large display and vertical camera system; Camera Control.',
    'Apple Intelligence features and longer battery life in a large format.',
  ],
  [
    '2024',
    'iPhone 16 Pro',
    '2024-09-20',
    '$999 / $1,099 / $1,299',
    'iOS 18',
    '6.3 in',
    'Grade 5 titanium, larger display and Camera Control.',
    'A18 Pro, 4K120 Dolby Vision and 5x telephoto on both Pro sizes.',
  ],
  [
    '2024',
    'iPhone 16 Pro Max',
    '2024-09-20',
    '$1,199 / $1,399 / $1,599',
    'iOS 18',
    '6.9 in',
    'Largest iPhone display at launch; titanium and Camera Control.',
    'A larger 6.9-inch screen and the longest battery life in the family.',
  ],
  [
    '2025',
    'iPhone 16e',
    '2025-02-28',
    '$599',
    'iOS 18.3.1',
    '6.1 in',
    'Matte glass rear, single camera, Action button and USB-C.',
    'Apple’s C1 modem debuted alongside A18, Apple Intelligence and a 48MP camera.',
  ],
  [
    '2025',
    'iPhone 17',
    '2025-09-19',
    '$799',
    'iOS 26',
    '6.3 in',
    'Aluminium design, Dynamic Island, Ceramic Shield 2.',
    'ProMotion reached the standard model; 48MP dual cameras and Center Stage front camera.',
  ],
  [
    '2025',
    'iPhone Air',
    '2025-09-19',
    '$999',
    'iOS 26',
    '6.5 in',
    'Exceptionally thin titanium frame with single rear camera.',
    'A new ultra-thin branch of the line, balancing a large display with a light build.',
  ],
  [
    '2025',
    'iPhone 17 Pro',
    '2025-09-19',
    '$1,099',
    'iOS 26',
    '6.3 in',
    'Aluminium unibody and plateau camera system.',
    'A19 Pro, advanced vapor-chamber cooling and 48MP Pro Fusion cameras.',
  ],
  [
    '2025',
    'iPhone 17 Pro Max',
    '2025-09-19',
    '$1,199',
    'iOS 26',
    '6.9 in',
    'Large aluminium unibody with expanded camera plateau.',
    'Largest battery capacity and 8x optical-quality telephoto range in the family.',
  ],
  [
    '2026',
    'iPhone 17e',
    '2026-03-11',
    '$699',
    'iOS 26.3.1',
    '6.1 in',
    'MagSafe and Ceramic Shield 2',
    'Apple’s C1X alongside A19, Apple Intelligence and a 48MP camera.',
  ],
  [
    '2026',
    'iPhone 18 Pro',
    '2026-09-18',
    '$1,099',
    'iOS 27',
    '6.3 in',
    'Pro design with variable-aperture main camera system.',
    'A20 Pro and variable aperture bring computational and optical control together.',
  ],
  [
    '2026',
    'iPhone 18 Pro Max',
    '2026-09-18',
    '$1,199',
    'iOS 27',
    '6.9 in',
    'Large Pro design with variable aperture and advanced camera array.',
    'The largest Pro model pairs A20 Pro with the latest camera architecture.',
  ],
  [
    '2026',
    'iPhone Duo',
    '2026-10-23',
    '$1,999',
    'iOS 27',
    '5.4 in outer / 7.6 in inner',
    'Book-style foldable, grade 5 titanium and precision hinge.',
    'Apple’s first foldable iPhone adapts iOS across two ProMotion displays.',
  ],
];
const details = {
  'iPhone 18 Pro':
    'Apple announced iPhone 18 Pro on September 9, 2026. Apple lists a 6.3-inch display and availability from September 18.',
  'iPhone 18 Pro Max':
    'Apple announced iPhone 18 Pro Max on September 9, 2026. Apple lists a 6.9-inch display and availability from September 18.',
  'iPhone Duo':
    'Apple announced the first foldable iPhone on September 9, 2026. It has a 5.4-inch outer display and a 7.6-inch inner display; availability began October 23.',
  'iPhone 17':
    'Apple announced iPhone 17 on September 9, 2025; availability began September 19. It introduced ProMotion on the standard model.',
  'iPhone Air':
    'Apple introduced iPhone Air on September 9, 2025; availability began September 19. Its 6.5-inch display and thin titanium design established a distinct product branch.',
  'iPhone 17e':
    'Announced March 02, 2026 and available March 11. Its original US price was $699; it shipped with iOS 26.3.1.',
};
const timeline = document.querySelector('#timeline'),
  jump = document.querySelector('.year-jumps');
// Add image URL and attribution URL for each model as they are curated.
// Kept static so the page makes no image-lookup API requests at runtime.
const officialImages = {
  'iPhone (1st generation)': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=131510',
    'https://cdsassets.apple.com/content/services/pub/image?productid=131510',
  ],
  'iPhone 3G': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=132035',
    'https://cdsassets.apple.com/content/services/pub/image?productid=132035',
  ],
  'iPhone 3GS': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=132537',
    'https://cdsassets.apple.com/content/services/pub/image?productid=132537',
  ],
  'iPhone 4': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=132927',
    'https://cdsassets.apple.com/content/services/pub/image?productid=132927',
  ],
  'iPhone 4s': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=133476',
    'https://cdsassets.apple.com/content/services/pub/image?productid=133476',
  ],
  'iPhone 5': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=133778',
    'https://cdsassets.apple.com/content/services/pub/image?productid=133778',
  ],
  'iPhone 5c': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=134094',
    'https://cdsassets.apple.com/content/services/pub/image?productid=134094',
  ],
  'iPhone 5s': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=134096',
    'https://cdsassets.apple.com/content/services/pub/image?productid=134096',
  ],
  'iPhone 6': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=134711',
    'https://cdsassets.apple.com/content/services/pub/image?productid=134711',
  ],
  'iPhone 6 Plus': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=134710',
    'https://cdsassets.apple.com/content/services/pub/image?productid=134710',
  ],
  'iPhone 6s': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=500016',
    'https://cdsassets.apple.com/content/services/pub/image?productid=500016',
  ],
  'iPhone 6s Plus': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=500040',
    'https://cdsassets.apple.com/content/services/pub/image?productid=500040',
  ],
  'iPhone SE (1st generation)': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=501343',
    'https://cdsassets.apple.com/content/services/pub/image?productid=501343',
  ],
  'iPhone 7': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=502272',
    'https://cdsassets.apple.com/content/services/pub/image?productid=502272',
  ],
  'iPhone 7 Plus': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=502287',
    'https://cdsassets.apple.com/content/services/pub/image?productid=502287',
  ],
  'iPhone 8': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=504266',
    'https://cdsassets.apple.com/content/services/pub/image?productid=504266',
  ],
  'iPhone 8 Plus': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=504267',
    'https://cdsassets.apple.com/content/services/pub/image?productid=504267',
  ],
  'iPhone X': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=504268',
    'https://cdsassets.apple.com/content/services/pub/image?productid=504268',
  ],
  'iPhone XS': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=505753',
    'https://cdsassets.apple.com/content/services/pub/image?productid=505753',
  ],
  'iPhone XS Max': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=505716',
    'https://cdsassets.apple.com/content/services/pub/image?productid=505716',
  ],
  'iPhone XR': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=505602&',
    'https://cdsassets.apple.com/content/services/pub/image?productid=505602',
  ],
  'iPhone 11': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=507882',
    'https://cdsassets.apple.com/content/services/pub/image?productid=507882',
  ],
  'iPhone 11 Pro': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=507808',
    'https://cdsassets.apple.com/content/services/pub/image?productid=507808',
  ],
  'iPhone 11 Pro Max': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=507845',
    'https://cdsassets.apple.com/content/services/pub/image?productid=507845',
  ],
  'iPhone SE (2nd generation)': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=509370',
    'https://cdsassets.apple.com/content/services/pub/image?productid=509370',
  ],
  'iPhone 12 mini': [
    'https://cdsassets.apple.com/live/I2F2FLC5/iphone/iphone-12-mini.png',
    'https://cdsassets.apple.com/live/I2F2FLC5/iphone/iphone-12-mini.png',
  ],
  'iPhone 12': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=300241',
    'https://cdsassets.apple.com/content/services/pub/image?productid=300241',
  ],
  'iPhone 12 Pro': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=300242',
    'https://cdsassets.apple.com/content/services/pub/image?productid=300242',
  ],
  'iPhone 12 Pro Max': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=300240',
    'https://cdsassets.apple.com/content/services/pub/image?productid=300240',
  ],
  'iPhone 13 mini': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=300426',
    'https://cdsassets.apple.com/content/services/pub/image?productid=300426',
  ],
  'iPhone 13': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=300428',
    'https://cdsassets.apple.com/content/services/pub/image?productid=300428',
  ],
  'iPhone 13 Pro': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=300429',
    'https://cdsassets.apple.com/content/services/pub/image?productid=300429',
  ],
  'iPhone 13 Pro Max': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=300430',
    'https://cdsassets.apple.com/content/services/pub/image?productid=300430',
  ],
  'iPhone SE (3rd generation)': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=300865',
    'https://cdsassets.apple.com/content/services/pub/image?productid=300865',
  ],
  'iPhone 14': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=300878',
    'https://cdsassets.apple.com/content/services/pub/image?productid=300878',
  ],
  'iPhone 14 Plus': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=300879',
    'https://cdsassets.apple.com/content/services/pub/image?productid=300879',
  ],
  'iPhone 14 Pro': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=300880',
    'https://cdsassets.apple.com/content/services/pub/image?productid=300880',
  ],
  'iPhone 14 Pro Max': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=300881',
    'https://cdsassets.apple.com/content/services/pub/image?productid=300881',
  ],
  'iPhone 15': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=300991',
    'https://cdsassets.apple.com/content/services/pub/image?productid=300991',
  ],
  'iPhone 15 Plus': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=301004',
    'https://cdsassets.apple.com/content/services/pub/image?productid=301004',
  ],
  'iPhone 15 Pro': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=300993',
    'https://cdsassets.apple.com/content/services/pub/image?productid=300993',
  ],
  'iPhone 15 Pro Max': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=301003',
    'https://cdsassets.apple.com/content/services/pub/image?productid=301003',
  ],
  'iPhone 16': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=301045',
    'https://cdsassets.apple.com/content/services/pub/image?productid=301045',
  ],
  'iPhone 16 Plus': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=301046',
    'https://cdsassets.apple.com/content/services/pub/image?productid=301046',
  ],
  'iPhone 16 Pro': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=301047',
    'https://cdsassets.apple.com/content/services/pub/image?productid=301047',
  ],
  'iPhone 16 Pro Max': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=301048',
    'https://cdsassets.apple.com/content/services/pub/image?productid=301048',
  ],
  'iPhone 16e': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=301076',
    'https://cdsassets.apple.com/content/services/pub/image?productid=301076',
  ],
  'iPhone 17': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=301247',
    'https://cdsassets.apple.com/content/services/pub/image?productid=301247',
  ],
  'iPhone Air': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=301244',
    'https://cdsassets.apple.com/content/services/pub/image?productid=301244',
  ],
  'iPhone 17 Pro': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=301245',
    'https://cdsassets.apple.com/content/services/pub/image?productid=301245',
  ],
  'iPhone 17 Pro Max': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=301246',
    'https://cdsassets.apple.com/content/services/pub/image?productid=301246',
  ],
  'iPhone 17e': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=301285',
    'https://cdsassets.apple.com/content/services/pub/image?productid=301285',
  ],
  'iPhone 18 Pro': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=301316',
    'https://cdsassets.apple.com/content/services/pub/image?productid=301316',
  ],
  'iPhone 18 Pro Max': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=301317',
    'https://cdsassets.apple.com/content/services/pub/image?productid=301317',
  ],
  'iPhone Duo': [
    'https://cdsassets.apple.com/content/services/pub/image?productid=301318',
    'https://cdsassets.apple.com/content/services/pub/image?productid=301318',
  ],
};
const years = [...new Set(rows.map((r) => r[0]))];
years.forEach((y) => {
  const a = document.createElement('a');
  a.href = `#year-${y}`;
  a.textContent = y;
  jump.append(a);
});
years.forEach((year) => {
  const era = document.createElement('section');
  era.className = 'era';
  era.id = `year-${year}`;
  era.innerHTML = `<header class="era-heading"><h2>${year}</h2></header>`;
  rows
    .filter((r) => r[0] === year)
    .forEach((r) => {
      const [y, name, date, price, ios, display, design, innovation] = r;
      const e = document.createElement('article');
      e.className = 'entry';
      e.id = 'model-' + name.toLowerCase().replace(/[^a-z0-9]+/g, '-');
      e.setAttribute('aria-expanded', 'false');
      const day = new Date(date + 'T12:00:00Z').toLocaleDateString('en-GB', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        timeZone: 'UTC',
      });
      const image = officialImages[name];
      e.innerHTML = `<div class="entry-card" tabindex="0" aria-label="Explore ${name}"><div class="device-image">${image?.[0] ? `<img loading="lazy" decoding="async" src="${image[0]}" alt="${name}, historical product photograph" onerror="this.remove();this.parentElement.querySelector('.image-credit').textContent='Verified product image unavailable'">${image[1] ? ` <a class="image-credit" href="${image[1]}" target="_blank" rel="noopener">Product photo · source</a>` : '<span class="image-credit"></span>'}` : `<span class="image-credit"></span>`}</div><div class="entry-copy"><div class="entry-top"><h3>${name}</h3><span class="entry-date">${day}</span></div><p class="entry-blurb">${innovation}</p><div class="specs"><div class="spec"><b>Launch price · US</b>${price}${price.includes('*') ? ' (with carrier contract)' : ''}</div><div class="spec"><b>Original software</b>${ios}</div><div class="spec"><b>Display</b>${display}</div><div class="spec"><b>Design signature</b>${design}</div></div><button class="expand" type="button" aria-expanded="false">Archive note</button><div class="more">${details[name] || innovation + ' ' + design + ' Original launch configuration and price varied by storage and market.'}</div></div></div>`;
      era.append(e);
    });
  timeline.append(era);
});
document.querySelectorAll('.entry').forEach((e) => {
  const toggle = () => {
    const open = e.getAttribute('aria-expanded') === 'true';
    e.setAttribute('aria-expanded', String(!open));
    e.querySelector('.expand').setAttribute('aria-expanded', String(!open));
  };
  e.querySelector('.entry-card').addEventListener('click', (ev) => {
    if (!ev.target.closest('a,button')) toggle();
  });
  e.querySelector('.entry-card').addEventListener('keydown', (ev) => {
    if ((ev.key === 'Enter' || ev.key === ' ') && ev.target.classList.contains('entry-card')) {
      ev.preventDefault();
      toggle();
    }
  });
  e.querySelector('.expand').addEventListener('click', (ev) => {
    ev.stopPropagation();
    toggle();
  });
});
const readout = document.querySelector('.year-readout'),
  bar = document.querySelector('.progress-bar'),
  timelineEl = document.querySelector('.timeline');
let ticking = false;
function update() {
  const rect = timelineEl.getBoundingClientRect(),
    total = timelineEl.offsetHeight - innerHeight,
    passed = Math.max(0, Math.min(total, -rect.top));
  const pct = total > 0 ? passed / total : 0;
  bar.style.width = pct * 100 + '%';
  timelineEl.style.setProperty('--progress', pct * 100 + '%');
  const active = [...document.querySelectorAll('.era')]
    .filter((s) => s.getBoundingClientRect().top < innerHeight * 0.45)
    .pop();
  if (active) readout.textContent = active.querySelector('h2').textContent;
  ticking = false;
}
window.addEventListener(
  'scroll',
  () => {
    if (!ticking) {
      requestAnimationFrame(update);
      ticking = true;
    }
  },
  { passive: true },
);
window.addEventListener('resize', update);
update();
