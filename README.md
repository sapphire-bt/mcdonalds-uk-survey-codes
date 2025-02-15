# McDonald's UK Survey Code Generator

An attempt to reverse engineer the 12 digit codes found on McDonald's receipts used for the [Food for Thoughts](https://www.mcdfoodforthoughts.com/) survey.

## Usage

Call the script with the following arguments:

```
get_code.py --store-id 1553 --order-id 1743 --purchased "2023-03-14 16:48"
```

The above will output `7ZWW-NGH3-ZFWJ` which matches the following receipt:

![Receipt showing code 7ZWW-NGH3-ZFWJ](./assets/7ZWW-NGH3-ZFWJ.jpg)

Note the receipt contains `REG 20` - this is the default value used in the script. If you're trying to reconstruct a receipt's code and it doesn't look right, try including the `--reg` flag with the reg number when calling the script.

A non-exhaustive list of store IDs is included (stores.tsv). You can also find store IDs by inspecting the return data from the [McDonald's store locator](https://www.mcdonalds.com/gb/en-gb/restaurant-locator.html) or by simply checking receipts from stores.

## About

The survey code above can be broken down as follows:

| Code    | Decimal   | Meaning                                                                                                                                |
| -       | -         | -                                                                                                                                      |
| `7ZW`   | 1553      | Store ID.                                                                                                                              |
| `WNG`   | 2043      | Usually seems to be a combination of the order ID's last two digits + the "reg" number multiplied by 100. In this case: 43 + 20 * 100. |
| `H3ZFW` | 3,742,128 | Date/time of purchase (represented as number of minutes since `2016-02-01 00:00`).                                                     |
| `J`     | 23        | Check digit (Luhn mod _N_ algorithm; uses 25 as a base).                                                                               |

Values are encoded using the following base 25 system:

<table>
    <tbody>
        <tr>
            <th>Decimal</th>
            <td>0</td>
            <td>1</td>
            <td>2</td>
            <td>3</td>
            <td>4</td>
            <td>5</td>
            <td>6</td>
            <td>7</td>
            <td>8</td>
            <td>9</td>
            <td>10</td>
            <td>11</td>
            <td>12</td>
            <td>13</td>
            <td>14</td>
            <td>15</td>
            <td>16</td>
            <td>17</td>
            <td>18</td>
            <td>19</td>
            <td>20</td>
            <td>21</td>
            <td>22</td>
            <td>23</td>
            <td>24</td>
        </tr>
        <tr>
            <th>Base 25</th>
            <td>C</td>
            <td>M</td>
            <td>7</td>
            <td>W</td>
            <td>D</td>
            <td>6</td>
            <td>N</td>
            <td>4</td>
            <td>R</td>
            <td>H</td>
            <td>F</td>
            <td>9</td>
            <td>Z</td>
            <td>L</td>
            <td>3</td>
            <td>X</td>
            <td>K</td>
            <td>Q</td>
            <td>G</td>
            <td>V</td>
            <td>P</td>
            <td>B</td>
            <td>T</td>
            <td>J</td>
            <td>Y</td>
        </tr>
    </tbody>
</table>

Further discussion on Reverse Engineering Stack Exchange where this was originally posted: https://reverseengineering.stackexchange.com/questions/32129/mcdonalds-receipt-codes

Also included is a .csv file containing several survey codes gathered for research (discussed in issue #13).

## "The survey isn't accepting generated codes"

The scripts in this repository produce technically valid codes, but not every code is accepted by the survey. I don't know why this is as there's no visibility into the survey's backend validation.

It's entirely possible that if you submit a code that looks like it was ordered via a drive-through from a store that doesn't actually have one, then they have some way of detecting that and rejecting the code.

If this happens, consider experimenting with different values before opening an issue saying "it's not working".

Although the survey asks for the amount spent, this does not form part of the 12 digit code and hasn't been required since at least August 2023.

## Confused?

If the above made no sense to you and/or you just want to generate a code, download this repository using the green "<> Code" button at the top of the page, open demo/page.html in a web browser on your computer/laptop, then fill out the parameters as required.
