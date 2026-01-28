"""
Account-specific writing styles to avoid Facebook detection.
Each account has a unique way of writing titles and descriptions.
"""

import random

class AccountWritingStyles:
    """Manages unique writing styles for each Facebook account."""

    def __init__(self, account_name):
        self.account_name = account_name
        self.style = self._get_style_for_account(account_name)

    def _get_style_for_account(self, account_name):
        """
        Assign a consistent writing style based on account name.
        Uses hash to ensure same account always gets same style.
        """
        # Get hash of account name to consistently assign style
        account_hash = sum(ord(c) for c in account_name.lower())
        style_index = account_hash % 5  # 5 different styles

        styles = {
            0: 'professional',
            1: 'casual',
            2: 'enthusiastic',
            3: 'minimalist',
            4: 'detailed'
        }

        return styles[style_index]

    def format_description(self, base_description, product_type='general'):
        """
        Format description according to account's unique style.

        Args:
            base_description: The base description content
            product_type: Type of product (carpet, grass, decking, etc.)

        Returns:
            Formatted description in account's unique style
        """
        if self.style == 'professional':
            return self._professional_style(base_description, product_type)
        elif self.style == 'casual':
            return self._casual_style(base_description, product_type)
        elif self.style == 'enthusiastic':
            return self._enthusiastic_style(base_description, product_type)
        elif self.style == 'minimalist':
            return self._minimalist_style(base_description, product_type)
        else:  # detailed
            return self._detailed_style(base_description, product_type)

    def _professional_style(self, base_desc, product_type):
        """Professional, formal writing style."""
        templates = [
            f"""PRODUCT SPECIFICATIONS:
{base_desc}

DELIVERY INFORMATION:
- Express delivery available (2-4 business days)
- Free samples provided upon request
- Professional installation service available

QUALITY ASSURANCE:
- Premium grade materials
- Certified for UK standards
- Backed by manufacturer warranty

Contact us for detailed specifications.""",

            f"""Professional Grade {product_type.title()}

{base_desc}

Service Details:
→ Fast UK delivery (2-4 days)
→ Complimentary samples available
→ Expert installation quotes provided

Quality Guaranteed
All products meet UK quality standards.

Enquiries welcome.""",

            f"""{base_desc}

Delivery: 2-4 working days nationwide
Samples: Available free of charge
Installation: Professional service offered

Quality assured. UK standards certified.
Contact for specifications."""
        ]

        return random.choice(templates)

    def _casual_style(self, base_desc, product_type):
        """Casual, friendly writing style."""
        templates = [
            f"""Hey! Check out this {product_type} :)

{base_desc}

Quick delivery - usually 2-4 days!
Free samples if you want to see it first
Can help with fitting too if needed

Any questions just ask! Happy to help.
Cheers""",

            f"""Great {product_type} available now!

{base_desc}

Delivery is pretty quick (2-4 days normally)
Can send you a free sample first if you like
Also do installation if you need it

Feel free to message with any questions
Thanks for looking!""",

            f"""{base_desc}

Gets to you in 2-4 days usually
Free samples available - just ask!
Can help with fitting if needed

Message me if you have any questions
Cheers!"""
        ]

        return random.choice(templates)

    def _enthusiastic_style(self, base_desc, product_type):
        """Enthusiastic, excited writing style with emojis."""
        templates = [
            f"""🌟 Amazing {product_type.title()}! 🌟

{base_desc}

✨ WHAT YOU GET:
🚚 Super fast delivery (2-4 days!)
📦 FREE samples - see before you buy!
🔧 Professional installation available!

Perfect for transforming your space! 💯

Message me - I'd love to help! 😊""",

            f"""⭐ TOP QUALITY {product_type.upper()}! ⭐

{base_desc}

🎯 THE BENEFITS:
✅ Quick delivery (2-4 days)
✅ Free samples sent out
✅ Installation help available

This will look AMAZING in your home! 🏡

Get in touch - happy to answer questions! 👍""",

            f"""🔥 Brilliant {product_type.title()} Deal! 🔥

{base_desc}

💪 Why choose this:
→ Fast delivery! (2-4 days)
→ Free samples! Try before you buy!
→ We can install too!

Transform your space today! ✨

Drop me a message! 💬"""
        ]

        return random.choice(templates)

    def _minimalist_style(self, base_desc, product_type):
        """Minimalist, concise writing style."""
        templates = [
            f"""{base_desc}

Delivery: 2-4 days
Samples: Free
Installation: Available

Contact for details.""",

            f"""{product_type.title()} Available

{base_desc}

- Fast delivery (2-4 days)
- Free samples
- Installation service offered

Message to order.""",

            f"""{base_desc}

Quick delivery.
Free samples available.
Installation help if needed.

Get in touch."""
        ]

        return random.choice(templates)

    def _detailed_style(self, base_desc, product_type):
        """Detailed, informative writing style."""
        templates = [
            f"""Comprehensive {product_type.title()} Solution

PRODUCT DESCRIPTION:
{base_desc}

ORDERING INFORMATION:
Our streamlined ordering process ensures quick dispatch, with most orders delivered within 2-4 working days. We understand that choosing the right product is important, which is why we offer complimentary samples - allowing you to see and feel the quality before making your purchase decision.

INSTALLATION SERVICES:
Professional installation services are available across the UK. Our experienced team can provide quotes and complete the installation to the highest standards.

CUSTOMER SUPPORT:
We pride ourselves on excellent customer service. Feel free to reach out with any questions about specifications, suitability, or installation requirements.

Quality products. Professional service. Competitive prices.""",

            f"""High-Quality {product_type.title()} - Detailed Information

{base_desc}

DELIVERY SERVICE:
We offer nationwide delivery with most orders dispatched within 24 hours and delivered in 2-4 working days. Track your order online for complete peace of mind.

FREE SAMPLE SERVICE:
Not sure if this is right for you? Request a free sample to examine the quality firsthand. Samples are dispatched quickly so you can make an informed decision.

PROFESSIONAL INSTALLATION:
Our network of professional installers covers the entire UK. We can arrange a site visit, provide a detailed quote, and complete the installation to the highest standards.

For more information or to place an order, please get in touch. We're here to help you find the perfect solution.""",

            f"""{product_type.title()} - Full Product Details

{base_desc}

Delivery Information:
Express delivery service available with 2-4 day delivery across the UK. Orders are carefully packaged to ensure products arrive in perfect condition.

Sample Request:
Free samples can be requested at any time. This allows you to assess the quality, texture, and suitability before committing to a purchase.

Installation Support:
Professional installation services available. Our installers are experienced and can complete the work efficiently and to a high standard.

Questions? Contact us anytime. We're happy to provide additional information, specifications, or advice on the best product for your needs."""
        ]

        return random.choice(templates)

    def get_title_prefix(self, product_type):
        """Get title prefix based on account style."""
        if self.style == 'professional':
            prefixes = ['Professional', 'Premium', 'Commercial Grade', 'Quality']
        elif self.style == 'casual':
            prefixes = ['Great', 'Lovely', 'Nice', 'Good Quality']
        elif self.style == 'enthusiastic':
            prefixes = ['Amazing', 'Brilliant', 'Fantastic', 'Superb']
        elif self.style == 'minimalist':
            prefixes = ['Quality', 'Standard', 'Good', 'Solid']
        else:  # detailed
            prefixes = ['High-Quality', 'Comprehensive', 'Complete', 'Full-Spec']

        return random.choice(prefixes)

    def get_title_suffix(self, product_type):
        """Get title suffix based on account style."""
        if self.style == 'professional':
            suffixes = ['| Professional Grade', '| Quality Assured', '| UK Standards']
        elif self.style == 'casual':
            suffixes = ['| Great Deal', '| Quick Delivery', '| Check It Out']
        elif self.style == 'enthusiastic':
            suffixes = ['| Amazing Quality!', '| Perfect Choice!', '| Top Rated!']
        elif self.style == 'minimalist':
            suffixes = ['', '| Available Now', '']
        else:  # detailed
            suffixes = ['| Full Details Available', '| Complete Service', '| Comprehensive Solution']

        return random.choice(suffixes)


# Example usage
if __name__ == "__main__":
    # Test different accounts
    accounts = ['john', 'mary', 'david', 'sarah', 'mike']

    for account in accounts:
        style_manager = AccountWritingStyles(account)
        print(f"\n{'='*60}")
        print(f"Account: {account} - Style: {style_manager.style}")
        print(f"{'='*60}")

        base_desc = """Premium quality artificial grass
Perfect for gardens, patios, and balconies
Low maintenance and long-lasting"""

        print(style_manager.format_description(base_desc, 'artificial grass'))
        print()
