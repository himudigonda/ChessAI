// frontend/src/components/utils.js

const files = 'abcdefgh';
const ranks = '87654321';

export function uciToCoords(uci) {
    const from = uci.slice(0, 2);
    const to = uci.slice(2, 4);
    return {
        fromFile: files.indexOf(from[0]),
        fromRank: ranks.indexOf(from[1]),
        toFile: files.indexOf(to[0]),
        toRank: ranks.indexOf(to[1])
    }
}