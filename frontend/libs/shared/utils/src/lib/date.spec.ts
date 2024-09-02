
import { extractTime } from './date.utils';

describe('extractTime', () => {
    it('should return the time in HH:MM format', () => {
        const date = new Date('2024-03-08T01:20:00');
        expect(extractTime(date)).toEqual('01:20');
    });

    it('should return time with leading zeros for single digits', () => {
        const date = new Date('2024-03-08T09:05:00');
        expect(extractTime(date)).toEqual('09:05');
    });
});
