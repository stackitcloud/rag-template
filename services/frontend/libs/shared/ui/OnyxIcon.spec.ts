import { mount } from '@vue/test-utils';

import OnyxIcon from './OnyxIcon.vue';

describe('OnyxIcon', () => {
  it('renders a valid svg string', () => {
    const wrapper = mount(OnyxIcon, {
      props: {
        icon: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><path d="M0 0h10v10H0z"/></svg>',
      },
    });

    expect(wrapper.find('svg').exists()).toBe(true);
    expect(wrapper.find('path').exists()).toBe(true);
  });

  it('removes event handler attributes', () => {
    const wrapper = mount(OnyxIcon, {
      props: {
        icon: '<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0h1v1H0z" onload="alert(1)"/></svg>',
      },
    });

    expect(wrapper.find('svg').exists()).toBe(true);
    expect(wrapper.find('path').attributes('onload')).toBeUndefined();
  });

  it('removes javascript: href attributes', () => {
    const wrapper = mount(OnyxIcon, {
      props: {
        icon: '<svg xmlns="http://www.w3.org/2000/svg"><a href="javascript:alert(1)">x</a></svg>',
      },
    });

    expect(wrapper.find('svg').exists()).toBe(true);
    expect(wrapper.find('a').attributes('href')).toBeUndefined();
    expect(wrapper.html()).not.toMatch(/javascript:/i);
  });

  it('removes javascript: xlink:href attributes', () => {
    const wrapper = mount(OnyxIcon, {
      props: {
        icon: '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"><a xlink:href="javascript:alert(1)">x</a></svg>',
      },
    });

    expect(wrapper.find('svg').exists()).toBe(true);
    expect(wrapper.html()).not.toMatch(/javascript:/i);
  });

  it('rejects script tags', () => {
    const wrapper = mount(OnyxIcon, {
      props: {
        icon: '<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>',
      },
    });

    expect(wrapper.find('svg').exists()).toBe(false);
  });

  it('rejects foreignObject content', () => {
    const wrapper = mount(OnyxIcon, {
      props: {
        icon: '<svg xmlns="http://www.w3.org/2000/svg"><foreignObject><div>hi</div></foreignObject></svg>',
      },
    });

    expect(wrapper.find('svg').exists()).toBe(false);
  });

  it('rejects non-svg input', () => {
    const wrapper = mount(OnyxIcon, {
      props: {
        icon: '<div>nope</div>',
      },
    });

    expect(wrapper.find('svg').exists()).toBe(false);
  });

  it('rejects malformed svg input', () => {
    const wrapper = mount(OnyxIcon, {
      props: {
        icon: '<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0h1v1H0z"/></sv>',
      },
    });

    expect(wrapper.find('svg').exists()).toBe(false);
  });

  it('rejects overly large svg strings', () => {
    const wrapper = mount(OnyxIcon, {
      props: {
        icon: `<svg xmlns="http://www.w3.org/2000/svg">${' '.repeat(100_000)}</svg>`,
      },
    });

    expect(wrapper.find('svg').exists()).toBe(false);
  });
});
