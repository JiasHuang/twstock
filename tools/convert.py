#!/usr/bin/python3

import os
import re
import argparse

html_text = '''
<html>
<script>
    // 1. Save scroll position to localStorage as the user scrolls
    window.addEventListener('scroll', () => {
      localStorage.setItem('scrollPosition', window.scrollY);
    });

    // 2. Restore scroll position automatically when the page loads
    window.addEventListener('load', () => {
      const savedPosition = localStorage.getItem('scrollPosition');
      if (savedPosition !== null) {
        window.scrollTo(0, parseInt(savedPosition, 10));
      }
    });
</script>
<body bgcolor="#bgcolor">
<style>
    pre {
        margin: #marginpx;
        font-size: #fontsizepx;
        color: #color;
    }
</style>
'''

def webp_to_jpg(src):
    dst = src + '.jpg'
    os.system('convert \'%s\' \'%s\'' %(src, dst))
    os.system('rm -f \'%s\'' %(src))
    return

def init_fo(f, args):
    fo = open(f, 'w')
    global html_text
    code = html_text
    code = code.replace('scrollPosition', os.path.basename(f) + '_scrollPosition')
    code = code.replace('#bgcolor', args.bgcolor)
    code = code.replace('#fontsize', str(args.fontsize))
    code = code.replace('#color', args.fontcolor)
    code = code.replace('#margin', str(args.margin))
    fo.write(code)
    return fo

def exit_fo(fo):
    fo.write('</body></html>')
    fo.close()

def encode_to_utf8(f):
    dst = os.path.join(os.path.basename(f))
    if dst != f:
        os.system('iconv -c -f gbk -t utf-8 {} -o {}'.format(f, dst))
    return dst

def txt_to_html(src, args):
    index = 0
    name = os.path.basename(src).split('.')[0]
    dstdir = name
    dst = name + '.html'
    if args.split:
        os.makedirs(dstdir, exist_ok=True)
        dst = os.path.join(dstdir, '{}_{:06d}.html'.format(name, 0))

    fo = init_fo(dst, args)
    with open(src, 'r') as fd:
        for line in fd.readlines():
            line = line.strip()
            total = len(line)
            offset = 0
            if total == 0:
                continue
            m = re.search(r'^第(.*)章', line)
            if m:
                index = index + 1
                if index % args.split == 0:
                    exit_fo(fo)
                    dst = os.path.join(dstdir, '{}_{:06d}.html'.format(name, index))
                    fo = init_fo(dst, args)
                fo.write('<hr><h1><a href="#{}">#{}</a></h1>\n'.format(index, index))
            fo.write('<pre>\n')
            while offset < total:
                num = min(total - offset, args.linewrap)
                fo.write(line[offset:offset + num] + '\n')
                offset += num
            fo.write('</pre><br>\n')
        exit_fo(fo)
    return

def extract_audio(url):
    m = re.search(r'https://www.youtube.com/watch\?v=[\w_-]*', url)
    if m:
        os.system('yt-dlp --cookies-from-browser chrome --extract-audio \'{}\''.format(m.group(0)))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bgcolor', default='#121212')
    parser.add_argument('--fontcolor', default='#b0b0b0')
    parser.add_argument('--fontsize', type=int, default=28)
    parser.add_argument('--linewrap', type=int, default=60)
    parser.add_argument('--margin', type=int, default=30)
    parser.add_argument('--split', type=int, default=100)
    parser.add_argument('--encode', action="store_true", default=False)
    args, unparsed = parser.parse_known_args()
    for f in unparsed:
        print(f)
        if f.startswith('https://'):
            extract_audio(f)
        elif f.endswith('.webp'):
            webp_to_jpg(f)
        elif f.endswith('.txt'):
            if args.encode:
                f = encode_to_utf8(f)
            txt_to_html(f, args)
    return

if __name__ == '__main__':
    main()
